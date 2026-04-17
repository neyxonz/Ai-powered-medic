from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session, current_app
from flask_login import login_required, current_user
from datetime import datetime
import json

from backend.database import db, Prescription, PrescriptionItem, Medicine, MedicalReport, Patient, Doctor, ActiveIngredient, MedicineIngredient

prescription_bp = Blueprint('prescription', __name__, url_prefix='/prescription')


# ===== دوال مساعدة =====
def check_prescription_access(prescription, user_role, current_user):
    """التحقق من صلاحية الوصول إلى الوصفة"""
    if user_role == 'doctor':
        return prescription.doctor_id == current_user.id
    elif user_role == 'patient':
        return prescription.patient_id == current_user.id
    return False


def get_medicine_by_name(med_name):
    """البحث عن دواء بالاسم (تجاري أو علمي)"""
    medicine = Medicine.query.filter(
        db.or_(
            Medicine.commercial_name.ilike(f"%{med_name}%"),
            Medicine.scientific_name.ilike(f"%{med_name}%")
        )
    ).first()
    return medicine


@prescription_bp.route('/<int:prescription_id>/view')
@login_required
def view_prescription(prescription_id):
    """عرض وصفة طبية للطباعة"""
    prescription = Prescription.query.get_or_404(prescription_id)
    
    # التحقق من الصلاحية
    user_role = session.get('user_role')
    
    if not check_prescription_access(prescription, user_role, current_user):
        flash('🔒 Unauthorized access', 'danger')
        if user_role == 'doctor':
            return redirect(url_for('doctor.doctor_dashboard'))
        return redirect(url_for('patient.patient_dashboard'))
    
    # جلب معلومات الطبيب والمريض
    doctor = Doctor.query.get(prescription.doctor_id)
    patient = Patient.query.get(prescription.patient_id)
    
    return render_template('doctor/view_prescription.html',
                         show_header=True,  
                         prescription=prescription,
                         doctor=doctor,
                         patient=patient,
                         datetime=datetime)


@prescription_bp.route('/<int:prescription_id>/print')
@login_required
def print_prescription(prescription_id):
    """طباعة وصفة طبية (نسخة مبسطة للطباعة)"""
    prescription = Prescription.query.get_or_404(prescription_id)
    
    # التحقق من الصلاحية
    user_role = session.get('user_role')
    
    if not check_prescription_access(prescription, user_role, current_user):
        flash('🔒 Unauthorized access', 'danger')
        if user_role == 'doctor':
            return redirect(url_for('doctor.doctor_dashboard'))
        return redirect(url_for('patient.patient_dashboard'))
    
    # جلب معلومات الطبيب والمريض
    doctor = Doctor.query.get(prescription.doctor_id)
    patient = Patient.query.get(prescription.patient_id)
    
    return render_template('doctor/print_prescription.html',
                         prescription=prescription,
                         doctor=doctor,
                         patient=patient,
                         datetime=datetime)


@prescription_bp.route('/api/medicine/<int:medicine_id>', methods=['GET'])
@login_required
def get_medicine_api(medicine_id):
    """API لجلب معلومات الدواء من قاعدة البيانات"""
    medicine = Medicine.query.get_or_404(medicine_id)
    
    return jsonify({
        'id': medicine.id,
        'scientific_name': medicine.scientific_name,
        'commercial_name': medicine.commercial_name,
        'category': medicine.category,
        'common_dosages': json.loads(medicine.common_dosages) if medicine.common_dosages else [],
        'contraindications': medicine.contraindications,
        'side_effects': medicine.side_effects
    })


@prescription_bp.route('/api/medicine/search', methods=['GET'])
@login_required
def search_medicine_api():
    """API للبحث عن الأدوية بالاسم"""
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify({'medicines': []})
    
    medicines = Medicine.query.filter(
        db.or_(
            Medicine.commercial_name.ilike(f"%{query}%"),
            Medicine.scientific_name.ilike(f"%{query}%")
        )
    ).limit(20).all()
    
    medicines_data = [{
        'id': m.id,
        'commercial_name': m.commercial_name,
        'scientific_name': m.scientific_name,
        'category': m.category
    } for m in medicines]
    
    return jsonify({'medicines': medicines_data})


@prescription_bp.route('/api/medicine/<int:medicine_id>/ingredients', methods=['GET'])
@login_required
def get_medicine_ingredients(medicine_id):
    """API لجلب المواد الفعالة لدواء معين"""
    medicine = Medicine.query.get_or_404(medicine_id)
    
    ingredients = []
    for med_ing in MedicineIngredient.query.filter_by(medicine_id=medicine_id).all():
        ingredient = med_ing.ingredient
        ingredients.append({
            'id': ingredient.id,
            'name': ingredient.name,
            'scientific_name': ingredient.scientific_name,
            'amount_mg': med_ing.amount_mg,
            'max_daily_dose_mg': ingredient.max_daily_dose_mg,
            'max_single_dose_mg': ingredient.max_single_dose_mg,
            'warning_message': ingredient.warning_message,
            'side_effects': ingredient.side_effects,
            'risk_factors': ingredient.risk_factors
        })
    
    return jsonify({
        'medicine': {
            'id': medicine.id,
            'commercial_name': medicine.commercial_name,
            'scientific_name': medicine.scientific_name
        },
        'ingredients': ingredients
    })


@prescription_bp.route('/api/patient/<int:patient_id>/active-ingredients', methods=['GET'])
@login_required
def get_patient_active_ingredients(patient_id):
    """API لجلب المواد الفعالة التي يتناولها المريض"""
    patient = Patient.query.get_or_404(patient_id)
    
    # التحقق من الصلاحية
    user_role = session.get('user_role')
    if user_role == 'doctor':
        if current_user not in patient.doctors:
            return jsonify({'error': 'Unauthorized'}), 403
    elif user_role == 'patient':
        if current_user.id != patient_id:
            return jsonify({'error': 'Unauthorized'}), 403
    else:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # جلب جميع التقارير
    reports = MedicalReport.query.filter_by(patient_id=patient_id).all()
    
    # استخراج الأدوية من التقارير
    all_medications = []
    for report in reports:
        all_medications.extend(report.get_medications())
    
    # البحث عن المواد الفعالة
    ingredients_found = {}
    for med_name in all_medications:
        # معالجة اسم الدواء (قد يكون نصاً أو قاموساً)
        if isinstance(med_name, dict):
            med_name = med_name.get('name', str(med_name))
        else:
            med_name = str(med_name)
        
        medicine = get_medicine_by_name(med_name)
        
        if medicine:
            for med_ing in MedicineIngredient.query.filter_by(medicine_id=medicine.id).all():
                ing = med_ing.ingredient
                if ing.name not in ingredients_found:
                    ingredients_found[ing.name] = {
                        'id': ing.id,
                        'name': ing.name,
                        'scientific_name': ing.scientific_name,
                        'total_daily_dose': 0,
                        'max_daily_dose_mg': ing.max_daily_dose_mg,
                        'warning_message': ing.warning_message
                    }
                ingredients_found[ing.name]['total_daily_dose'] += med_ing.amount_mg
    
    return jsonify(list(ingredients_found.values()))


@prescription_bp.route('/api/patient/<int:patient_id>/reports', methods=['GET'])
@login_required
def get_patient_reports_api(patient_id):
    """API لجلب تقارير المريض لفحص التداخلات"""
    patient = Patient.query.get_or_404(patient_id)
    
    # التحقق من الصلاحية
    user_role = session.get('user_role')
    if user_role == 'doctor':
        if current_user not in patient.doctors:
            return jsonify({'error': 'Unauthorized'}), 403
    elif user_role == 'patient':
        if current_user.id != patient_id:
            return jsonify({'error': 'Unauthorized'}), 403
    else:
        return jsonify({'error': 'Unauthorized'}), 403
    
    reports = MedicalReport.query.filter_by(patient_id=patient_id)\
                .order_by(MedicalReport.report_date.desc()).all()
    
    reports_data = []
    for report in reports:
        # معالجة الأدوية للتأكد من صحة التنسيق
        medications = report.get_medications()
        if medications and isinstance(medications, list):
            medications = [str(m) if not isinstance(m, dict) else m.get('name', str(m)) for m in medications]
        
        reports_data.append({
            'id': report.id,
            'conditions': report.get_conditions(),
            'medications': medications,
            'alerts': report.get_alerts(),
            'summary': report.summary,
            'date': report.report_date.strftime('%Y-%m-%d'),
            'doctor_id': report.doctor_id
        })
    
    return jsonify(reports_data)


# ===== API إضافية للوصفات =====

@prescription_bp.route('/api/patient/<int:patient_id>/prescriptions', methods=['GET'])
@login_required
def get_patient_prescriptions_api(patient_id):
    """API لجلب جميع الوصفات الطبية للمريض"""
    patient = Patient.query.get_or_404(patient_id)
    
    # التحقق من الصلاحية
    user_role = session.get('user_role')
    if user_role == 'doctor':
        if current_user not in patient.doctors:
            return jsonify({'error': 'Unauthorized'}), 403
    elif user_role == 'patient':
        if current_user.id != patient_id:
            return jsonify({'error': 'Unauthorized'}), 403
    else:
        return jsonify({'error': 'Unauthorized'}), 403
    
    prescriptions = Prescription.query.filter_by(patient_id=patient_id)\
                     .order_by(Prescription.created_at.desc()).all()
    
    prescriptions_data = []
    for p in prescriptions:
        doctor = Doctor.query.get(p.doctor_id)
        prescriptions_data.append({
            'id': p.id,
            'date': p.created_at.strftime('%Y-%m-%d'),
            'diagnosis': p.diagnosis,
            'notes': p.notes,
            'is_active': p.is_active,
            'doctor_name': doctor.name if doctor else 'Unknown',
            'items': [{
                'medicine': item.medicine.commercial_name if item.medicine else 'Unknown',
                'dosage': item.dosage,
                'frequency': item.frequency,
                'duration': item.duration,
                'instructions': item.instructions
            } for item in p.items]
        })
    
    return jsonify({'prescriptions': prescriptions_data})


@prescription_bp.route('/api/check-interactions', methods=['POST'])
@login_required
def check_interactions_api():
    """API لفحص التداخلات الدوائية"""
    data = request.json
    medicine_ids = data.get('medicine_ids', [])
    patient_id = data.get('patient_id')
    
    if not medicine_ids:
        return jsonify({'interactions': [], 'warning': 'No medicines to check'})
    
    # جلب المواد الفعالة للأدوية الجديدة
    new_ingredients = set()
    for med_id in medicine_ids:
        medicine = Medicine.query.get(med_id)
        if medicine:
            for med_ing in MedicineIngredient.query.filter_by(medicine_id=med_id).all():
                new_ingredients.add(med_ing.ingredient.name)
    
    # جلب المواد الفعالة الحالية للمريض
    current_ingredients = set()
    if patient_id:
        patient = Patient.query.get(patient_id)
        if patient:
            reports = MedicalReport.query.filter_by(patient_id=patient_id).all()
            for report in reports:
                for med_name in report.get_medications():
                    if isinstance(med_name, dict):
                        med_name = med_name.get('name', str(med_name))
                    medicine = get_medicine_by_name(str(med_name))
                    if medicine:
                        for med_ing in MedicineIngredient.query.filter_by(medicine_id=medicine.id).all():
                            current_ingredients.add(med_ing.ingredient.name)
    
    # البحث عن التداخلات (بسيط - يمكن توسيعه)
    interactions = []
    common = new_ingredients.intersection(current_ingredients)
    if common:
        interactions.append({
            'type': 'duplicate',
            'message': f'Patient is already taking medications containing: {", ".join(common)}',
            'severity': 'warning'
        })
    
    return jsonify({
        'interactions': interactions,
        'new_ingredients': list(new_ingredients),
        'current_ingredients': list(current_ingredients)
    })


@prescription_bp.route('/<int:prescription_id>/deactivate', methods=['POST'])
@login_required
def deactivate_prescription(prescription_id):
    """إلغاء تنشيط وصفة طبية"""
    prescription = Prescription.query.get_or_404(prescription_id)
    user_role = session.get('user_role')
    
    # فقط الطبيب يمكنه إلغاء تنشيط الوصفة
    if user_role != 'doctor' or prescription.doctor_id != current_user.id:
        flash('🔒 Unauthorized access', 'danger')
        return redirect(url_for('doctor.doctor_dashboard'))
    
    prescription.is_active = False
    db.session.commit()
    
    flash(f'✅ Prescription #{prescription_id} has been deactivated', 'success')
    return redirect(url_for('doctor.patient_reports', patient_id=prescription.patient_id))

@prescription_bp.route('/api/analyze-prescription/<int:patient_id>', methods=['POST'])
@login_required
def analyze_prescription_with_ai(patient_id):
    """
    تحليل الوصفة الطبية - نسخة مبسطة تعمل 100%
    """
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        # التحقق من صلاحية الطبيب
        user_role = session.get('user_role')
        if user_role == 'doctor':
            if current_user not in patient.doctors:
                return jsonify({'error': 'Unauthorized'}), 403
        elif user_role == 'patient':
            if current_user.id != patient.id:
                return jsonify({'error': 'Unauthorized'}), 403
        else:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        medications = data.get('medications', [])
        
        # ===== معلومات المريض الأساسية =====
        patient_info = {
            'name': patient.name,
            'age': patient.age or 0,
            'gender': patient.gender or 'Not specified',
            'chronic_conditions': patient.chronic_conditions or 'None',
            'allergies': patient.allergies or 'None',
            'current_medications': patient.current_medications or 'None'
        }
        
        # ===== معلومات الأدوية =====
        medications_info = []
        for med in medications:
            medicine_id = med.get('medicine_id')
            if medicine_id:
                medicine = Medicine.query.get(medicine_id)
                if medicine:
                    medications_info.append({
                        'id': medicine.id,
                        'name': medicine.commercial_name,
                        'scientific_name': medicine.scientific_name,
                        'category': medicine.category or 'Unknown',
                        'requested_dosage': med.get('dosage', ''),
                        'requested_frequency': med.get('frequency', '')
                    })
        
        # ✅ إرجاع البيانات بنجاح
        return jsonify({
            'success': True,
            'patient_profile': patient_info,
            'medications_info': medications_info
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in analyze_prescription_with_ai: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500