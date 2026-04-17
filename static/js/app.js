// ============================================================================
// AI-Powered Medic - Main Application
// TABLE OF CONTENTS
// ============================================================================
//
// ===== 1. analyzeReports: دالة تحليل التقارير الطبية (عدة صور) =====
// ===== 2. addEventListener: ربط النماذج في الصفحات المختلفة =====
// ===== 3. openFullscreen: دالة عرض الصور في وضع الفول سكرين =====
// ===== 4. createAccountCheckbox =====
// ===== 5. showLogin: دالة تبديل واجهة تسجيل الدخول بين المريض والطبيب =====
// ===== 6. checkDrugInteractions: دالة كشف تداخل الأدوية المتقدمة =====
// ===== 7. analyzeDosageSafety: دالة تحليل الجرعات =====
// ===== 8. displayDosageAnalysis: دالة عرض تحليل الجرعات =====
// ===== 9. onMedicationsChange: دالة لفحص التداخلات عند تغيير الأدوية =====
//
//=============================================================================
// ===== 1. analyzeReports =====
async function analyzeReports(imageFiles, patientId = null) {
    const status = document.getElementById("analysisStatus");
    const resultBox = document.getElementById("analysisResult");
    
    if (!imageFiles || imageFiles.length === 0) {
        alert("Please select at least one file");
        return;
    }

    status.style.display = "block";
    status.textContent = `📤 Processing ${imageFiles.length} image(s)...`;
    status.className = "status-message info";
    
    if (resultBox) resultBox.style.display = "none";

    let allText = "";
    let successCount = 0;
    let errorCount = 0;
    let firstImagePath = null;
    let imagePaths = [];  // مصفوفة لتخزين كل الصور

    for (let i = 0; i < imageFiles.length; i++) {
        const file = imageFiles[i];
        
        status.textContent = `📤 Processing image ${i+1} of ${imageFiles.length}: ${file.name}`;
        
        const formData = new FormData();
        formData.append("file", file);

        try {
            // 1. OCR لكل صورة
            const ocrResponse = await fetch("/ocr", {
                method: "POST",
                body: formData
            });

            if (!ocrResponse.ok) {
                errorCount++;
                console.error(`OCR failed for ${file.name}`);
                continue;
            }

            const ocrData = await ocrResponse.json();
            
            // جمع النصوص معاً
            allText += `\n\n--- Page ${i+1}: ${file.name} ---\n${ocrData.text}\n`;
            
            // خزن أول صورة كمرجع
            if (i === 0) {
                firstImagePath = ocrData.image_path;
            }
            
            // ✅ تخزين مسار كل صورة
            imagePaths.push(ocrData.image_path);
            
            successCount++;
            
        } catch (error) {
            console.error(`Error processing ${file.name}:`, error);
            errorCount++;
        }
    }

    if (successCount === 0) {
        status.textContent = "❌ No images could be processed";
        status.className = "status-message error";
        return;
    }

    // 2. إرسال النص الكامل للـ AI
    status.textContent = `🔍 Analyzing ${successCount} images with AI...`;

    const prompt = `Extract medical information from this complete medical report (multiple pages combined) and return JSON.

Complete Medical Report:
${allText}

Return exactly this format:
{
    "conditions": [],
    "medications": [],
    "alerts": [],
    "summary": ""
}`;

    try {
        // 3. استدعاء puter.ai
        const aiResponse = await puter.ai.chat(prompt);
        console.log("AI response:", aiResponse);

        // 4. تحويل الرد
        let analysis;
        try {
            let content;
            if (aiResponse.message && aiResponse.message.content) {
                content = aiResponse.message.content;
            } else if (aiResponse.content) {
                content = aiResponse.content;
            } else if (typeof aiResponse === 'string') {
                content = aiResponse;
            } else {
                content = JSON.stringify(aiResponse);
            }
            
            analysis = JSON.parse(content);
            
            analysis.conditions = analysis.conditions || [];
            analysis.medications = analysis.medications || [];
            analysis.alerts = analysis.alerts || [];
            analysis.summary = analysis.summary || "No summary provided";
            
        } catch (e) {
            console.log("Parse error, using raw response:", e);
            analysis = { 
                summary: typeof aiResponse === 'string' ? aiResponse : JSON.stringify(aiResponse),
                conditions: [],
                medications: [],
                alerts: []
            };
        }

        // 5. عرض النتائج للمستخدم
        if (resultBox) {
            resultBox.style.display = "block";
            
            const tableBody = document.getElementById("resultTableBody");
            
            if (tableBody) {
                // عرض في جدول (للمريض والطبيب)
                const currentDate = new Date().toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                });
                
                const conditionsList = analysis.conditions?.map(c => `• ${c}`).join('<br>') || 'None identified';
                const medicationsList = analysis.medications?.map(m => `• ${m}`).join('<br>') || 'None identified';
                const alertsList = analysis.alerts?.map(a => `⚠️ ${a}`).join('<br>') || 'None';
                
                tableBody.innerHTML = `
                    <tr>
                        <td class="date-cell">${currentDate}</td>
                        <td>${conditionsList}</td>
                        <td>${medicationsList}</td>
                        <td>${alertsList}</td>
                        <td class="summary-cell">${analysis.summary || 'No summary available'}</td>
                    </tr>
                `;
                
                const statsHTML = `<p>✅ Processed: ${successCount} of ${imageFiles.length} images</p>`;
                resultBox.innerHTML = statsHTML + resultBox.innerHTML;
                
            } else {
                // عرض عادي (للصفحة الرئيسية)
                let resultsHTML = '<h3>📋 Analysis Results</h3>';
                
                resultsHTML += '<p><strong>Conditions:</strong> ' + 
                    (analysis.conditions?.join(', ') || 'None identified') + '</p>';
                
                resultsHTML += '<p><strong>Medications:</strong> ' + 
                    (analysis.medications?.join(', ') || 'None identified') + '</p>';
                
                resultsHTML += '<p><strong>Alerts:</strong> ' + 
                    (analysis.alerts?.map(a => '⚠️ ' + a).join(', ') || 'None') + '</p>';
                
                resultsHTML += '<p><strong>Summary:</strong> ' + 
                    (analysis.summary || 'No summary available') + '</p>';
                
                resultBox.innerHTML = resultsHTML;
            }
        }

        status.textContent = "✅ Analysis complete!";

        // 6. حفظ في قاعدة البيانات
        if (patientId && imagePaths.length > 0) {
            const saveResponse = await fetch("/save-report", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    patient_id: patientId,
                    image_paths: imagePaths,
                    conditions: analysis.conditions || [],
                    medications: analysis.medications || [],
                    alerts: analysis.alerts || [],
                    summary: analysis.summary || "Analysis complete"
                })
            });
            
            if (saveResponse.ok) {
                status.textContent = "✅ Saved!";
            }
        }

    } catch (error) {
        console.error("Error:", error);
        status.textContent = "❌ Error: " + error.message;
        status.className = "status-message error";
    }
}

// ===== 2. addEventListener =====
document.addEventListener("DOMContentLoaded", function() {
    // الصفحة الرئيسية (للزوار)
    const quickForm = document.getElementById("quickAnalysisForm");
    if (quickForm) {
        quickForm.addEventListener("submit", function(e) {
            e.preventDefault();
            const files = document.getElementById("quickReportImage").files;
            analyzeReports(files);
        });
    }
    
    // صفحة المريض
    const patientForm = document.getElementById("patientUploadForm");
    if (patientForm) {
        patientForm.addEventListener("submit", function(e) {
            e.preventDefault();
            const files = document.getElementById("patientReportImage").files;  // 👈 patientReportImage
            const patientId = document.getElementById("patientId").value;
            analyzeReports(files, patientId);
        });
    }

    // صفحة الطبيب
    const doctorForm = document.getElementById("doctorAnalyzeForm");
    if (doctorForm) {
        doctorForm.addEventListener("submit", function(e) {
            e.preventDefault();
            const files = document.getElementById("doctorReportImage").files;  // 👈 doctorReportImage
            const patientId = document.getElementById("patientId").value;
            analyzeReports(files, patientId);
        });
    }
});

// ===== 3. openFullscreen =====
function openFullscreen(img) {
    // إذا كان العنصر هو زر، نجيب الصورة
    if (img.tagName === 'BUTTON') {
        img = img.closest('.image-container')?.querySelector('img');
    }
    
    if (!img) return alert("Image not found");
    
    // نبحث عن المودال أو ننشئه
    let modal = document.getElementById('imageModal');
    
   if (!modal) {
    modal = document.createElement('div');
    modal.id = 'imageModal';
    modal.className = 'modal';
    modal.innerHTML = '<span class="close-modal" onclick="this.parentElement.style.display=\'none\'">&times;</span><img class="modal-content">';
    modal.onclick = (e) => e.target === modal ? modal.style.display = 'none' : null;
    document.body.appendChild(modal);
}
    
    // عرض الصورة
    modal.querySelector('img').src = img.src;
    modal.style.display = 'block';
}


// ===== 4. createAccountCheckbox =====
const createAccountCheckbox = document.getElementById('createAccountCheckbox');
if (createAccountCheckbox) {
    createAccountCheckbox.addEventListener('change', function() {
        const accountFields = document.getElementById('accountFields');
        if (accountFields) {
            accountFields.style.display = this.checked ? 'block' : 'none';
        }
        
        const ssnInput = document.querySelector('input[name="ssn"]');
        const passwordInput = document.querySelector('input[name="password"]');
        
        if (this.checked) {
            if (ssnInput) ssnInput.required = true;
            if (passwordInput) passwordInput.required = true;
        } else {
            if (ssnInput) ssnInput.required = false;
            if (passwordInput) passwordInput.required = false;
        }
    });
}

// ===== 5. showLogin =====
function showLogin(type) {
    const ssnField = document.getElementById('ssnField');
    const emailField = document.getElementById('emailField');
    const submitBtn = document.getElementById('submitBtn');
    const userType = document.getElementById('userType');
    const patientBtn = document.getElementById('patientBtn');
    const doctorBtn = document.getElementById('doctorBtn');
    
    // تحقق من وجود العناصر قبل استخدامها
    if (!ssnField || !emailField || !submitBtn || !userType || !patientBtn || !doctorBtn) {
        console.log("Login elements not found on this page");
        return;
    }
    
    if (type === 'patient') {
        ssnField.style.display = 'block';
        emailField.style.display = 'none';
        submitBtn.textContent = 'Login as Patient';
        patientBtn.style.background = '#3b82f6';
        doctorBtn.style.background = '#64748b';
        userType.value = 'patient';
    } else {
        ssnField.style.display = 'none';
        emailField.style.display = 'block';
        submitBtn.textContent = 'Login as Doctor';
        patientBtn.style.background = '#64748b';
        doctorBtn.style.background = '#3b82f6';
        userType.value = 'doctor';
    }
}
// ===== 6. checkDrugInteractions =====
async function checkDrugInteractions(patientId, selectedMedications) {
    const alertsContainer = document.getElementById('aiAlerts');
    const alertsContent = document.getElementById('aiAlertsContent');
    
    try {
        // 1. جلب التقارير السابقة للمريض
        const reportsResponse = await fetch(`/api/patient/${patientId}/reports`);
        const reports = await reportsResponse.json();
        
        // 2. استخراج الأدوية السابقة والتحذيرات
        let previousMedications = [];
        let previousAlerts = [];
        let patientConditions = [];
        
        reports.forEach(report => {
            if (report.medications && report.medications.length > 0) {
                report.medications.forEach(med => {
                    if (typeof med === 'string') {
                        previousMedications.push(med);
                    } else {
                        previousMedications.push(med.name || med);
                    }
                });
            }
            if (report.alerts && report.alerts.length > 0) {
                previousAlerts.push(...report.alerts);
            }
            if (report.conditions && report.conditions.length > 0) {
                patientConditions.push(...report.conditions);
            }
        });
        
        // 3. جلب معلومات الأدوية
        let medicinesInfo = [];
        for (let med of selectedMedications) {
            try {
                const medResponse = await fetch(`/api/medicine/${med.medicine_id}`);
                const medData = await medResponse.json();
                medicinesInfo.push({
                    name: medData.commercial_name,
                    dosage: med.dosage,
                    frequency: med.frequency
                });
            } catch(e) {
                medicinesInfo.push({ name: med.name, dosage: med.dosage, frequency: med.frequency });
            }
        }
        
        // 4. Prompt مختصر
        const prompt = `
أجب فقط بـ JSON. لا تكتب أي شرح خارج JSON.

حلل التفاعلات بين:
- الأدوية الحالية: ${previousMedications.slice(0, 5).join(', ') || 'لا يوجد'}
- الأدوية الجديدة: ${medicinesInfo.map(m => m.name).join(', ')}

أعد JSON:
{
    "interactions": [
        {
            "type": "drug-drug",
            "description": "وصف مختصر بسطر واحد",
            "severity": "high/medium/low",
            "medicines_involved": ["دواء1", "دواء2"],
            "recommendation": "توصية مختصرة بسطر واحد"
        }
    ],
    "summary": "ملخص مختصر بسطر واحد",
    "safe_to_prescribe": true/false
}

قواعد:
1. أقصى طول لكل وصف: 100 حرف
2. إذا لم توجد تفاعلات، أرجع مصفوفة فارغة
`;

        // 5. استدعاء الذكاء الاصطناعي
        const aiResponse = await puter.ai.chat(prompt);
        
        // 6. تحليل الرد
        let result;
        try {
            let content = aiResponse.content || aiResponse;
            if (typeof content === 'string') {
                content = content.replace(/```json/g, '').replace(/```/g, '').trim();
                result = JSON.parse(content);
            } else {
                result = content;
            }
        } catch(e) {
            console.error("Error parsing AI response:", e);
            result = {
                interactions: [],
                summary: "تعذر تحليل التفاعلات",
                safe_to_prescribe: true
            };
        }
        
        // 7. عرض النتائج
        if (alertsContainer && alertsContent) {
            alertsContainer.style.display = 'block';
            
            if (result.interactions && result.interactions.length > 0) {
                let alertsHtml = '';
                const highSeverity = result.interactions.filter(i => i.severity === 'high');
                const mediumSeverity = result.interactions.filter(i => i.severity === 'medium');
                const lowSeverity = result.interactions.filter(i => i.severity === 'low');
                
                if (highSeverity.length > 0) {
                    alertsHtml += '<div class="alert-high"><h5><i class="fas fa-exclamation-triangle"></i> تحذيرات خطيرة</h5>';
                    highSeverity.forEach(i => {
                        alertsHtml += `
                            <div class="interaction-item">
                                <strong>⚠️ ${i.description}</strong>
                                <p>📌 ${i.recommendation}</p>
                                <small>💊 ${i.medicines_involved?.join(', ') || ''}</small>
                            </div>
                        `;
                    });
                    alertsHtml += '</div>';
                }
                
                if (mediumSeverity.length > 0) {
                    alertsHtml += '<div class="alert-medium"><h5><i class="fas fa-exclamation-circle"></i> تنبيهات</h5>';
                    mediumSeverity.forEach(i => {
                        alertsHtml += `
                            <div class="interaction-item">
                                <strong>⚠️ ${i.description}</strong>
                                <p>📌 ${i.recommendation}</p>
                            </div>
                        `;
                    });
                    alertsHtml += '</div>';
                }
                
                if (lowSeverity.length > 0) {
                    alertsHtml += '<div class="alert-low"><h5><i class="fas fa-info-circle"></i> ملاحظات</h5>';
                    lowSeverity.forEach(i => {
                        alertsHtml += `<div class="interaction-item">ℹ️ ${i.description}</div>`;
                    });
                    alertsHtml += '</div>';
                }
                
                alertsHtml += `<div class="interaction-summary"><strong>الملخص:</strong> ${result.summary}</div>`;
                
                if (!result.safe_to_prescribe) {
                    alertsHtml += '<div class="not-safe-warning"><i class="fas fa-ban"></i> الوصفة غير آمنة! يرجى المراجعة.</div>';
                }
                
                alertsContent.innerHTML = alertsHtml;
            } else {
                alertsContent.innerHTML = '<div class="no-interactions"><i class="fas fa-check-circle"></i> لا توجد تفاعلات دوائية خطيرة</div>';
            }
        }
        
        return result;
        
    } catch (error) {
        console.error("Error checking interactions:", error);
        if (alertsContainer && alertsContent) {
            alertsContainer.style.display = 'block';
            alertsContent.innerHTML = '<div class="error-message"><i class="fas fa-times-circle"></i> حدث خطأ في فحص التداخلات</div>';
        }
        return { interactions: [], summary: "خطأ", safe_to_prescribe: true };
    }
}

// ===== 7. analyzeDosageSafety =====
async function analyzeDosageSafety(patientId, selectedMedications) {
    const dosageAnalysisDiv = document.getElementById('dosageAnalysis');
    
    try {
        // جلب المواد الفعالة للأدوية الجديدة
        let allNewIngredients = [];
        for (let med of selectedMedications) {
            try {
                const response = await fetch(`/api/medicine/${med.medicine_id}/ingredients`);
                const ingredients = await response.json();
                allNewIngredients.push(...ingredients);
            } catch(e) {
                console.error('Error fetching ingredients:', e);
            }
        }
        
        // تجميع وتحليل الجرعات
        const groupedIngredients = {};
        allNewIngredients.forEach(ing => {
            if (!groupedIngredients[ing.name]) {
                groupedIngredients[ing.name] = {
                    name: ing.name,
                    total_daily_dose: 0,
                    max_daily_dose_mg: ing.max_daily_dose_mg,
                    warning_message: ing.warning_message
                };
            }
            // تقدير الجرعة اليومية (افتراض مرتين في اليوم)
            groupedIngredients[ing.name].total_daily_dose += (ing.amount_mg || 0) * 2;
        });
        
        // عرض التحليل
        if (dosageAnalysisDiv && typeof displayDosageAnalysis === 'function') {
            dosageAnalysisDiv.style.display = 'block';
            displayDosageAnalysis(groupedIngredients);
        }
        
        return { analysis: groupedIngredients };
        
    } catch (error) {
        console.error("Error analyzing dosage:", error);
        if (dosageAnalysisDiv) {
            dosageAnalysisDiv.style.display = 'block';
            const tableBody = document.getElementById('dosageTableBody');
            if (tableBody) {
                tableBody.innerHTML = `<tr><td colspan="5" class="text-center">خطأ في تحليل الجرعات</td></tr>`;
            }
        }
        return { analysis: {} };
    }
}

// ===== 8. displayDosageAnalysis =====
function displayDosageAnalysis(analysis) {
    const tableBody = document.getElementById('dosageTableBody');
    const summaryDiv = document.getElementById('dosageSummary');
    const statusBadge = document.getElementById('dosageStatus');
    
    if (!tableBody) return;
    
    if (!analysis || Object.keys(analysis).length === 0) {
        tableBody.innerHTML = `<tr><td colspan="5" class="text-center">لا توجد مواد فعالة للتحليل</td></tr>`;
        return;
    }
    
    let hasDanger = false;
    let hasWarning = false;
    let totalIngredients = 0;
    let safeCount = 0;
    
    let html = '';
    for (const [name, data] of Object.entries(analysis)) {
        totalIngredients++;
        const isSafe = data.total_daily_dose <= data.max_daily_dose_mg;
        let statusClass = 'safe';
        let statusText = '✅ ضمن الحد';
        
        if (!isSafe) {
            if (data.total_daily_dose > data.max_daily_dose_mg * 1.5) {
                statusClass = 'danger';
                statusText = '🔴 تجاوز خطير';
                hasDanger = true;
            } else {
                statusClass = 'warning';
                statusText = '⚠️ تجاوز الحد';
                hasWarning = true;
            }
        } else {
            safeCount++;
        }
        
        html += `
            <tr class="dosage-row ${statusClass}">
                <td><strong>${name}</strong></td>
                <td>${data.total_daily_dose} mg</td>
                <td>${data.max_daily_dose_mg} mg</td>
                <td><span class="dosage-status ${statusClass}">${statusText}</span></td>
                <td class="warning-cell">${!isSafe ? (data.warning_message || '⚠️ تجاوز الجرعة الآمنة') : '—'}</td>
            </tr>
        `;
    }
    
    tableBody.innerHTML = html;
    
    // تحديث الملخص
    if (summaryDiv) {
        let summaryClass = 'safe';
        let summaryText = 'جميع الجرعات ضمن الحد الآمن';
        
        if (hasDanger) {
            summaryClass = 'danger';
            summaryText = `⚠️ ${totalIngredients - safeCount} مادة تتجاوز الجرعة الآمنة بشكل خطير`;
        } else if (hasWarning) {
            summaryClass = 'warning';
            summaryText = `⚠️ ${totalIngredients - safeCount} مادة تتجاوز الجرعة الآمنة`;
        }
        
        summaryDiv.innerHTML = `
            <div class="summary-stats">
                <div class="stat-card ${summaryClass}">
                    <i class="fas ${summaryClass === 'danger' ? 'fa-exclamation-triangle' : (summaryClass === 'warning' ? 'fa-exclamation-circle' : 'fa-check-circle')}"></i>
                    <div class="stat-info">
                        <span class="stat-label">الحالة العامة</span>
                        <span class="stat-value">${summaryText}</span>
                    </div>
                </div>
                <div class="stat-card">
                    <i class="fas fa-capsules"></i>
                    <div class="stat-info">
                        <span class="stat-label">المواد الفعالة</span>
                        <span class="stat-value">${totalIngredients}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    if (statusBadge) {
        let badgeClass = 'safe';
        if (hasDanger) badgeClass = 'danger';
        else if (hasWarning) badgeClass = 'warning';
        statusBadge.className = `analysis-badge ${badgeClass}`;
    }
}

// ===== 9. onMedicationsChange =====
async function onMedicationsChange(patientId) {
    const medicineSelects = document.querySelectorAll('.medicine-select');
    const dosageSelects = document.querySelectorAll('.dosage-select');
    const frequencyInputs = document.querySelectorAll('.frequency-input');
    const durationInputs = document.querySelectorAll('.duration-input');
    
    const selectedMedications = [];
    
    for (let i = 0; i < medicineSelects.length; i++) {
        const medSelect = medicineSelects[i];
        if (medSelect.value) {
            selectedMedications.push({
                medicine_id: medSelect.value,
                name: medSelect.options[medSelect.selectedIndex]?.text.split(' (')[0] || '',
                dosage: dosageSelects[i]?.value || '',
                frequency: frequencyInputs[i]?.value || '',
                duration: durationInputs[i]?.value || ''
            });
        }
    }
    
    if (selectedMedications.length > 0 && patientId) {
        // عرض مؤشر التحميل
        const alertsContainer = document.getElementById('aiAlerts');
        if (alertsContainer) {
            alertsContainer.style.display = 'block';
            const alertsContent = document.getElementById('aiAlertsContent');
            if (alertsContent) {
                alertsContent.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> جاري فحص التداخلات الدوائية...</div>';
            }
        }
        
        // ✅ فحص التداخلات الدوائية
        await checkDrugInteractions(patientId, selectedMedications);
        
        // ✅ فحص الجرعات
        await analyzeDosageSafety(patientId, selectedMedications);
        
    } else if (selectedMedications.length === 0) {
        const alertsContainer = document.getElementById('aiAlerts');
        const dosageAnalysis = document.getElementById('dosageAnalysis');
        if (alertsContainer) alertsContainer.style.display = 'none';
        if (dosageAnalysis) dosageAnalysis.style.display = 'none';
    }
}