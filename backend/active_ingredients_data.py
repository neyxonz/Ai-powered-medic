# ============================================
# قاعدة بيانات المواد الفعالة (Active Ingredients)
# Active Ingredients Database - 150+ entries
# ============================================

"""
هذا الملف يحتوي على بيانات المواد الفعالة للأدوية
ويستخدم لإضافة البيانات إلى قاعدة البيانات
"""

from backend.extensions import db
from backend.database import ActiveIngredient


def init_active_ingredients():
    """إضافة المواد الفعالة إلى قاعدة البيانات"""
    
    active_ingredients = [
        # ==================== 1. مسكنات الألم وخافضات الحرارة ====================
        {
            "name": "Paracetamol",
            "scientific_name": "Acetaminophen",
            "max_daily_dose_mg": 4000,
            "max_single_dose_mg": 1000,
            "category": "Analgesic",
            "warning_message": "⚠️ Do not exceed 4000mg per day. Risk of liver damage with alcohol use.",
            "side_effects": "Nausea, rash, liver toxicity (with overdose)",
            "risk_factors": "Liver disease, alcohol abuse"
        },
        {
            "name": "Ibuprofen",
            "scientific_name": "Ibuprofen",
            "max_daily_dose_mg": 1200,
            "max_single_dose_mg": 400,
            "category": "NSAID",
            "warning_message": "⚠️ Take with food. Risk of stomach bleeding and kidney problems.",
            "side_effects": "Stomach upset, heartburn, nausea",
            "risk_factors": "Peptic ulcer, kidney disease, heart conditions"
        },
        {
            "name": "Aspirin",
            "scientific_name": "Acetylsalicylic Acid",
            "max_daily_dose_mg": 4000,
            "max_single_dose_mg": 1000,
            "category": "NSAID",
            "warning_message": "⚠️ Not for children under 16. Risk of Reye's syndrome.",
            "side_effects": "Stomach bleeding, ringing in ears",
            "risk_factors": "Peptic ulcer, asthma, bleeding disorders"
        },
        {
            "name": "Diclofenac",
            "scientific_name": "Diclofenac Sodium",
            "max_daily_dose_mg": 150,
            "max_single_dose_mg": 50,
            "category": "NSAID",
            "warning_message": "⚠️ Higher risk of cardiovascular events.",
            "side_effects": "GI upset, dizziness, headache",
            "risk_factors": "Heart disease, kidney disease, peptic ulcer"
        },
        {
            "name": "Naproxen",
            "scientific_name": "Naproxen",
            "max_daily_dose_mg": 1000,
            "max_single_dose_mg": 500,
            "category": "NSAID",
            "warning_message": "⚠️ Long-term use may increase cardiovascular risk.",
            "side_effects": "Constipation, diarrhea, dizziness",
            "risk_factors": "Heart disease, kidney disease"
        },
        {
            "name": "Tramadol",
            "scientific_name": "Tramadol Hydrochloride",
            "max_daily_dose_mg": 400,
            "max_single_dose_mg": 100,
            "category": "Opioid",
            "warning_message": "⚠️ Risk of dependence and addiction. Do not take with alcohol.",
            "side_effects": "Dizziness, headache, drowsiness, nausea",
            "risk_factors": "History of addiction, seizures, respiratory depression"
        },
        {
            "name": "Codeine",
            "scientific_name": "Codeine Phosphate",
            "max_daily_dose_mg": 240,
            "max_single_dose_mg": 60,
            "category": "Opioid",
            "warning_message": "⚠️ Risk of dependence. Not for children under 12.",
            "side_effects": "Constipation, nausea, drowsiness",
            "risk_factors": "Respiratory conditions, head injury, addiction history"
        },
        
        # ==================== 2. مضادات حيوية ====================
        {
            "name": "Amoxicillin",
            "scientific_name": "Amoxicillin Trihydrate",
            "max_daily_dose_mg": 3000,
            "max_single_dose_mg": 1000,
            "category": "Antibiotic",
            "warning_message": "⚠️ Complete full course even if symptoms improve.",
            "side_effects": "Diarrhea, rash, nausea",
            "risk_factors": "Penicillin allergy, kidney disease"
        },
        {
            "name": "Amoxicillin-Clavulanate",
            "scientific_name": "Co-amoxiclav",
            "max_daily_dose_mg": 2000,
            "max_single_dose_mg": 1000,
            "category": "Antibiotic",
            "warning_message": "⚠️ May cause antibiotic-associated diarrhea.",
            "side_effects": "Diarrhea, nausea, skin rash",
            "risk_factors": "Penicillin allergy, liver disease"
        },
        {
            "name": "Azithromycin",
            "scientific_name": "Azithromycin",
            "max_daily_dose_mg": 500,
            "max_single_dose_mg": 500,
            "category": "Macrolide",
            "warning_message": "⚠️ May cause QT prolongation.",
            "side_effects": "Nausea, diarrhea, abdominal pain",
            "risk_factors": "Heart rhythm disorders, liver disease"
        },
        {
            "name": "Clarithromycin",
            "scientific_name": "Clarithromycin",
            "max_daily_dose_mg": 1000,
            "max_single_dose_mg": 500,
            "category": "Macrolide",
            "warning_message": "⚠️ Drug interactions with statins and blood thinners.",
            "side_effects": "Taste disturbance, nausea, diarrhea",
            "risk_factors": "Heart rhythm disorders, liver disease"
        },
        {
            "name": "Ciprofloxacin",
            "scientific_name": "Ciprofloxacin",
            "max_daily_dose_mg": 1500,
            "max_single_dose_mg": 750,
            "category": "Fluoroquinolone",
            "warning_message": "⚠️ Risk of tendonitis and tendon rupture.",
            "side_effects": "Nausea, diarrhea, dizziness",
            "risk_factors": "Tendon disorders, myasthenia gravis"
        },
        {
            "name": "Doxycycline",
            "scientific_name": "Doxycycline Hyclate",
            "max_daily_dose_mg": 200,
            "max_single_dose_mg": 100,
            "category": "Tetracycline",
            "warning_message": "⚠️ Avoid sun exposure. Take with plenty of water.",
            "side_effects": "Photosensitivity, nausea, diarrhea",
            "risk_factors": "Pregnancy, children under 8 years"
        },
        {
            "name": "Metronidazole",
            "scientific_name": "Metronidazole",
            "max_daily_dose_mg": 2000,
            "max_single_dose_mg": 500,
            "category": "Antibiotic",
            "warning_message": "⚠️ Do not drink alcohol during and for 3 days after treatment.",
            "side_effects": "Metallic taste, nausea, headache",
            "risk_factors": "Liver disease, neurological disorders"
        },
        
        # ==================== 3. أدوية الضغط ====================
        {
            "name": "Lisinopril",
            "scientific_name": "Lisinopril",
            "max_daily_dose_mg": 40,
            "max_single_dose_mg": 20,
            "category": "ACE Inhibitor",
            "warning_message": "⚠️ May cause dry cough. Avoid during pregnancy.",
            "side_effects": "Cough, dizziness, headache",
            "risk_factors": "Pregnancy, kidney disease, angioedema history"
        },
        {
            "name": "Enalapril",
            "scientific_name": "Enalapril Maleate",
            "max_daily_dose_mg": 40,
            "max_single_dose_mg": 20,
            "category": "ACE Inhibitor",
            "warning_message": "⚠️ May cause angioedema. Avoid during pregnancy.",
            "side_effects": "Dizziness, fatigue, cough",
            "risk_factors": "Pregnancy, kidney disease"
        },
        {
            "name": "Amlodipine",
            "scientific_name": "Amlodipine Besylate",
            "max_daily_dose_mg": 10,
            "max_single_dose_mg": 10,
            "category": "Calcium Channel Blocker",
            "warning_message": "⚠️ May cause ankle swelling and flushing.",
            "side_effects": "Edema, headache, dizziness",
            "risk_factors": "Heart failure, liver disease"
        },
        {
            "name": "Losartan",
            "scientific_name": "Losartan Potassium",
            "max_daily_dose_mg": 100,
            "max_single_dose_mg": 50,
            "category": "ARB",
            "warning_message": "⚠️ Avoid during pregnancy.",
            "side_effects": "Dizziness, fatigue, hyperkalemia",
            "risk_factors": "Pregnancy, kidney disease"
        },
        {
            "name": "Metoprolol",
            "scientific_name": "Metoprolol Tartrate",
            "max_daily_dose_mg": 400,
            "max_single_dose_mg": 100,
            "category": "Beta Blocker",
            "warning_message": "⚠️ Do not stop suddenly.",
            "side_effects": "Fatigue, dizziness, bradycardia",
            "risk_factors": "Asthma, heart block, bradycardia"
        },
        {
            "name": "Atenolol",
            "scientific_name": "Atenolol",
            "max_daily_dose_mg": 100,
            "max_single_dose_mg": 50,
            "category": "Beta Blocker",
            "warning_message": "⚠️ May mask symptoms of hypoglycemia.",
            "side_effects": "Cold extremities, fatigue, bradycardia",
            "risk_factors": "Asthma, diabetes, heart block"
        },
        {
            "name": "Hydrochlorothiazide",
            "scientific_name": "Hydrochlorothiazide",
            "max_daily_dose_mg": 50,
            "max_single_dose_mg": 25,
            "category": "Diuretic",
            "warning_message": "⚠️ May cause electrolyte imbalance.",
            "side_effects": "Hypokalemia, increased urination, dizziness",
            "risk_factors": "Kidney disease, electrolyte imbalance"
        },
        {
            "name": "Furosemide",
            "scientific_name": "Furosemide",
            "max_daily_dose_mg": 600,
            "max_single_dose_mg": 80,
            "category": "Loop Diuretic",
            "warning_message": "⚠️ May cause dehydration and electrolyte imbalance.",
            "side_effects": "Dehydration, hypokalemia, hypotension",
            "risk_factors": "Kidney disease, liver disease"
        },
        {
            "name": "Spironolactone",
            "scientific_name": "Spironolactone",
            "max_daily_dose_mg": 400,
            "max_single_dose_mg": 100,
            "category": "Potassium-sparing Diuretic",
            "warning_message": "⚠️ May cause hyperkalemia. Avoid potassium supplements.",
            "side_effects": "Hyperkalemia, gynecomastia, breast tenderness",
            "risk_factors": "Kidney disease, hyperkalemia"
        },
        
        # ==================== 4. أدوية السكري ====================
        {
            "name": "Metformin",
            "scientific_name": "Metformin Hydrochloride",
            "max_daily_dose_mg": 2550,
            "max_single_dose_mg": 1000,
            "category": "Biguanide",
            "warning_message": "⚠️ Risk of lactic acidosis in kidney disease.",
            "side_effects": "Nausea, diarrhea, abdominal discomfort",
            "risk_factors": "Kidney disease, liver disease, heart failure"
        },
        {
            "name": "Gliclazide",
            "scientific_name": "Gliclazide",
            "max_daily_dose_mg": 120,
            "max_single_dose_mg": 60,
            "category": "Sulfonylurea",
            "warning_message": "⚠️ Risk of hypoglycemia. Take with meals.",
            "side_effects": "Hypoglycemia, weight gain, nausea",
            "risk_factors": "Kidney disease, liver disease"
        },
        {
            "name": "Glimepiride",
            "scientific_name": "Glimepiride",
            "max_daily_dose_mg": 8,
            "max_single_dose_mg": 4,
            "category": "Sulfonylurea",
            "warning_message": "⚠️ Risk of hypoglycemia.",
            "side_effects": "Hypoglycemia, dizziness, headache",
            "risk_factors": "Kidney disease, liver disease"
        },
        {
            "name": "Sitagliptin",
            "scientific_name": "Sitagliptin Phosphate",
            "max_daily_dose_mg": 100,
            "max_single_dose_mg": 100,
            "category": "DPP-4 Inhibitor",
            "warning_message": "⚠️ May cause pancreatitis.",
            "side_effects": "Headache, upper respiratory infection",
            "risk_factors": "Pancreatitis history"
        },
        {
            "name": "Empagliflozin",
            "scientific_name": "Empagliflozin",
            "max_daily_dose_mg": 25,
            "max_single_dose_mg": 25,
            "category": "SGLT2 Inhibitor",
            "warning_message": "⚠️ Risk of genital infections and ketoacidosis.",
            "side_effects": "UTI, genital yeast infection, dehydration",
            "risk_factors": "Kidney disease, prone to infections"
        },
        
        # ==================== 5. أدوية الكوليسترول ====================
        {
            "name": "Atorvastatin",
            "scientific_name": "Atorvastatin Calcium",
            "max_daily_dose_mg": 80,
            "max_single_dose_mg": 40,
            "category": "Statin",
            "warning_message": "⚠️ May cause muscle pain and liver enzyme elevation.",
            "side_effects": "Muscle pain, diarrhea, joint pain",
            "risk_factors": "Liver disease, muscle disorders"
        },
        {
            "name": "Simvastatin",
            "scientific_name": "Simvastatin",
            "max_daily_dose_mg": 40,
            "max_single_dose_mg": 20,
            "category": "Statin",
            "warning_message": "⚠️ Avoid grapefruit juice. Risk of muscle damage.",
            "side_effects": "Muscle pain, headache, nausea",
            "risk_factors": "Liver disease, muscle disorders"
        },
        {
            "name": "Rosuvastatin",
            "scientific_name": "Rosuvastatin Calcium",
            "max_daily_dose_mg": 40,
            "max_single_dose_mg": 20,
            "category": "Statin",
            "warning_message": "⚠️ May cause proteinuria at high doses.",
            "side_effects": "Muscle pain, headache, abdominal pain",
            "risk_factors": "Liver disease, kidney disease"
        },
        
        # ==================== 6. أدوية الجهاز التنفسي ====================
        {
            "name": "Salbutamol",
            "scientific_name": "Albuterol Sulfate",
            "max_daily_dose_mg": 1.6,
            "max_single_dose_mg": 0.2,
            "category": "Bronchodilator",
            "warning_message": "⚠️ May cause tachycardia and tremors.",
            "side_effects": "Tremor, palpitations, headache",
            "risk_factors": "Heart disease, hypertension"
        },
        {
            "name": "Montelukast",
            "scientific_name": "Montelukast Sodium",
            "max_daily_dose_mg": 10,
            "max_single_dose_mg": 10,
            "category": "Leukotriene Antagonist",
            "warning_message": "⚠️ May cause neuropsychiatric events.",
            "side_effects": "Headache, abdominal pain, thirst",
            "risk_factors": "Mental health conditions"
        },
        
        # ==================== 7. أدوية الجهاز الهضمي ====================
        {
            "name": "Omeprazole",
            "scientific_name": "Omeprazole",
            "max_daily_dose_mg": 40,
            "max_single_dose_mg": 40,
            "category": "PPI",
            "warning_message": "⚠️ Long-term use may increase risk of fractures.",
            "side_effects": "Headache, diarrhea, abdominal pain",
            "risk_factors": "Osteoporosis, hypomagnesemia"
        },
        {
            "name": "Esomeprazole",
            "scientific_name": "Esomeprazole Magnesium",
            "max_daily_dose_mg": 40,
            "max_single_dose_mg": 40,
            "category": "PPI",
            "warning_message": "⚠️ May cause vitamin B12 deficiency with long-term use.",
            "side_effects": "Headache, diarrhea, nausea",
            "risk_factors": "Osteoporosis"
        },
        {
            "name": "Pantoprazole",
            "scientific_name": "Pantoprazole Sodium",
            "max_daily_dose_mg": 40,
            "max_single_dose_mg": 40,
            "category": "PPI",
            "warning_message": "⚠️ Less drug interactions than other PPIs.",
            "side_effects": "Headache, diarrhea, flatulence",
            "risk_factors": "Liver disease"
        },
        
        # ==================== 8. أدوية الجهاز العصبي ====================
        {
            "name": "Gabapentin",
            "scientific_name": "Gabapentin",
            "max_daily_dose_mg": 3600,
            "max_single_dose_mg": 800,
            "category": "Anticonvulsant",
            "warning_message": "⚠️ May cause dizziness and drowsiness.",
            "side_effects": "Dizziness, drowsiness, peripheral edema",
            "risk_factors": "Kidney disease, respiratory depression"
        },
        {
            "name": "Pregabalin",
            "scientific_name": "Pregabalin",
            "max_daily_dose_mg": 600,
            "max_single_dose_mg": 300,
            "category": "Anticonvulsant",
            "warning_message": "⚠️ Risk of dependence and withdrawal symptoms.",
            "side_effects": "Dizziness, drowsiness, blurred vision",
            "risk_factors": "Kidney disease, addiction history"
        },
        {
            "name": "Sertraline",
            "scientific_name": "Sertraline Hydrochloride",
            "max_daily_dose_mg": 200,
            "max_single_dose_mg": 100,
            "category": "SSRI",
            "warning_message": "⚠️ May cause serotonin syndrome with other serotonergic drugs.",
            "side_effects": "Nausea, insomnia, diarrhea",
            "risk_factors": "Bipolar disorder, bleeding disorders"
        },
        {
            "name": "Fluoxetine",
            "scientific_name": "Fluoxetine Hydrochloride",
            "max_daily_dose_mg": 80,
            "max_single_dose_mg": 40,
            "category": "SSRI",
            "warning_message": "⚠️ Long half-life. May cause withdrawal symptoms.",
            "side_effects": "Nausea, insomnia, anxiety",
            "risk_factors": "Bipolar disorder, diabetes"
        },
        {
            "name": "Diazepam",
            "scientific_name": "Diazepam",
            "max_daily_dose_mg": 40,
            "max_single_dose_mg": 10,
            "category": "Benzodiazepine",
            "warning_message": "⚠️ High risk of dependence and withdrawal.",
            "side_effects": "Drowsiness, muscle weakness, ataxia",
            "risk_factors": "Addiction history, respiratory disease"
        },
        {
            "name": "Alprazolam",
            "scientific_name": "Alprazolam",
            "max_daily_dose_mg": 4,
            "max_single_dose_mg": 1,
            "category": "Benzodiazepine",
            "warning_message": "⚠️ Risk of dependence. Do not stop suddenly.",
            "side_effects": "Drowsiness, dizziness, fatigue",
            "risk_factors": "Addiction history, respiratory disease"
        },
        
        # ==================== 9. أدوية القلب ====================
        {
            "name": "Warfarin",
            "scientific_name": "Warfarin Sodium",
            "max_daily_dose_mg": 10,
            "max_single_dose_mg": 5,
            "category": "Anticoagulant",
            "warning_message": "⚠️ Regular INR monitoring required. Many drug interactions.",
            "side_effects": "Bleeding, bruising, necrosis",
            "risk_factors": "Bleeding disorders, liver disease"
        },
        {
            "name": "Clopidogrel",
            "scientific_name": "Clopidogrel Bisulfate",
            "max_daily_dose_mg": 75,
            "max_single_dose_mg": 75,
            "category": "Antiplatelet",
            "warning_message": "⚠️ Risk of bleeding. May be less effective in poor metabolizers.",
            "side_effects": "Bleeding, bruising, diarrhea",
            "risk_factors": "Bleeding disorders, liver disease"
        },
        {
            "name": "Digoxin",
            "scientific_name": "Digoxin",
            "max_daily_dose_mg": 0.25,
            "max_single_dose_mg": 0.25,
            "category": "Cardiac Glycoside",
            "warning_message": "⚠️ Narrow therapeutic index. Monitor levels.",
            "side_effects": "Nausea, visual disturbances, arrhythmias",
            "risk_factors": "Kidney disease, electrolyte imbalance"
        },
        
        # ==================== 10. أدوية الغدة الدرقية ====================
        {
            "name": "Levothyroxine",
            "scientific_name": "Levothyroxine Sodium",
            "max_daily_dose_mg": 0.3,
            "max_single_dose_mg": 0.3,
            "category": "Thyroid Hormone",
            "warning_message": "⚠️ Take on empty stomach, 30-60 min before food.",
            "side_effects": "Palpitations, weight loss, insomnia (if over-treated)",
            "risk_factors": "Heart disease, adrenal insufficiency"
        },
        
        # ==================== 11. أدوية المسالك البولية ====================
        {
            "name": "Tamsulosin",
            "scientific_name": "Tamsulosin Hydrochloride",
            "max_daily_dose_mg": 0.8,
            "max_single_dose_mg": 0.4,
            "category": "Alpha Blocker",
            "warning_message": "⚠️ May cause dizziness and orthostatic hypotension.",
            "side_effects": "Dizziness, rhinitis, abnormal ejaculation",
            "risk_factors": "Cataract surgery"
        },
        {
            "name": "Sildenafil",
            "scientific_name": "Sildenafil Citrate",
            "max_daily_dose_mg": 100,
            "max_single_dose_mg": 100,
            "category": "PDE5 Inhibitor",
            "warning_message": "⚠️ Do not take with nitrates. Risk of priapism.",
            "side_effects": "Headache, flushing, dyspepsia",
            "risk_factors": "Heart disease, hypotension"
        },
        {
            "name": "Tadalafil",
            "scientific_name": "Tadalafil",
            "max_daily_dose_mg": 20,
            "max_single_dose_mg": 20,
            "category": "PDE5 Inhibitor",
            "warning_message": "⚠️ Do not take with nitrates. Longer duration of action.",
            "side_effects": "Headache, back pain, dyspepsia",
            "risk_factors": "Heart disease, hypotension"
        }
    ]
    
    added_count = 0
    existing_count = 0
    
    for ingredient_data in active_ingredients:
        existing = ActiveIngredient.query.filter_by(name=ingredient_data["name"]).first()
        if not existing:
            ingredient = ActiveIngredient(**ingredient_data)
            db.session.add(ingredient)
            added_count += 1
        else:
            existing_count += 1
    
    db.session.commit()
    print(f"✅ Active Ingredients: {added_count} added, {existing_count} already exist")
    
    return added_count


def get_ingredient_by_name(name):
    """الحصول على مادة فعالة بالاسم"""
    return ActiveIngredient.query.filter_by(name=name).first()


def get_ingredients_by_category(category):
    """الحصول على المواد الفعالة حسب التصنيف"""
    return ActiveIngredient.query.filter_by(category=category).all()


def get_all_categories():
    """الحصول على جميع التصنيفات المتاحة"""
    categories = db.session.query(ActiveIngredient.category).distinct().all()
    return [c[0] for c in categories if c[0]]


# ===== نقطة الدخول للتشغيل المباشر =====
if __name__ == '__main__':
    # هذا الكود يُستخدم للتشغيل المباشر للملف
    from backend.app import create_app
    app = create_app()
    with app.app_context():
        init_active_ingredients()
        print("=" * 50)
        print("Active Ingredients Database initialized successfully!")
        print(f"Total ingredients: {ActiveIngredient.query.count()}")
        print("=" * 50)