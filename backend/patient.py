from flask import Blueprint, render_template, redirect, url_for, flash, session, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime

from backend.database import db, MedicalReport, Prescription, PrescriptionItem, Doctor, Patient

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')


# ===== دوال مساعدة =====
def get_patient_doctors(patient):
    """الحصول على قائمة أطباء المريض"""
    return patient.doctors.all() if hasattr(patient.doctors, 'all') else list(patient.doctors)


def get_patient_stats(patient_id):
    """الحصول على إحصائيات المريض"""
    reports_count = MedicalReport.query.filter_by(patient_id=patient_id).count()
    prescriptions_count = Prescription.query.filter_by(patient_id=patient_id).count()
    
    # عدد الأطباء
    patient = Patient.query.get(patient_id)
    doctors_count = len(get_patient_doctors(patient)) if patient else 0
    
    # آخر تقرير
    latest_report = MedicalReport.query.filter_by(patient_id=patient_id)\
                      .order_by(MedicalReport.report_date.desc()).first()
    
    # عدد التنبيهات
    alerts_count = 0
    reports = MedicalReport.query.filter_by(patient_id=patient_id).all()
    for report in reports:
        alerts_count += len(report.get_alerts())
    
    return {
        'reports_count': reports_count,
        'prescriptions_count': prescriptions_count,
        'doctors_count': doctors_count,
        'alerts_count': alerts_count,
        'latest_report_date': latest_report.report_date if latest_report else None
    }


@patient_bp.route('/dashboard')
@login_required
def patient_dashboard():
    """لوحة تحكم المريض - عرض جميع التقارير والوصفات والإحصائيات"""
    if session.get('user_role') != 'patient':
        flash('🔒 Unauthorized access', 'danger')
        return redirect(url_for('home'))
    
    # جلب التقارير
    reports = MedicalReport.query.filter_by(patient_id=current_user.id)\
                .order_by(MedicalReport.report_date.desc()).all()
    
    # جلب الوصفات الطبية
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id)\
                     .order_by(Prescription.created_at.desc()).all()
    
    # جلب أطباء المريض
    doctors = get_patient_doctors(current_user)
    
    # الإحصائيات
    stats = get_patient_stats(current_user.id)
    
    # جلب التنبيهات من جميع التقارير
    all_alerts = []
    for report in reports[:5]:  # آخر 5 تقارير فقط
        alerts = report.get_alerts()
        for alert in alerts:
            if isinstance(alert, dict):
                all_alerts.append({
                    'message': alert.get('message', str(alert)),
                    'date': report.report_date,
                    'report_id': report.id
                })
            else:
                all_alerts.append({
                    'message': str(alert),
                    'date': report.report_date,
                    'report_id': report.id
                })
    
    # آخر 3 تقارير للعرض السريع
    recent_reports = reports[:3]
    
    return render_template('patient/patient_dashboard.html',
                         show_header=True,
                         patient=current_user,
                         reports=reports,
                         recent_reports=recent_reports,
                         prescriptions=prescriptions,
                         doctors=doctors,
                         stats=stats,
                         all_alerts=all_alerts,
                         datetime=datetime)


@patient_bp.route('/reports')
@login_required
def patient_reports_list():
    """عرض جميع تقارير المريض (صفحة منفصلة)"""
    if session.get('user_role') != 'patient':
        flash('🔒 Unauthorized access', 'danger')
        return redirect(url_for('home'))
    
    # معلمات البحث والفلترة
    search_query = request.args.get('search', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    sort_by = request.args.get('sort', 'date_desc')
    
    query = MedicalReport.query.filter_by(patient_id=current_user.id)
    
    # البحث
    if search_query:
        query = query.filter(
            db.or_(
                MedicalReport.summary.ilike(f'%{search_query}%'),
                MedicalReport.conditions.ilike(f'%{search_query}%'),
                MedicalReport.medications.ilike(f'%{search_query}%')
            )
        )
    
    # فلترة حسب التاريخ
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(MedicalReport.report_date >= from_date)
        except:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(MedicalReport.report_date <= to_date)
        except:
            pass
    
    # ترتيب النتائج
    if sort_by == 'date_desc':
        query = query.order_by(MedicalReport.report_date.desc())
    elif sort_by == 'date_asc':
        query = query.order_by(MedicalReport.report_date.asc())
    elif sort_by == 'doctor':
        query = query.order_by(MedicalReport.doctor_id)
    
    reports = query.all()
    
    # إحصائيات سريعة
    stats = {
        'total': len(reports),
        'with_conditions': sum(1 for r in reports if r.conditions and r.conditions != '[]'),
        'with_medications': sum(1 for r in reports if r.medications and r.medications != '[]')
    }
    
    return render_template('patient/patient_report.html',
                         show_header=True,
                         patient=current_user,
                         reports=reports,
                         stats=stats,
                         search_query=search_query,
                         date_from=date_from,
                         date_to=date_to,
                         sort_by=sort_by,
                         datetime=datetime)


@patient_bp.route('/report/<int:report_id>')
@login_required
def view_report(report_id):
    """عرض تفاصيل تقرير طبي محدد"""
    report = MedicalReport.query.get_or_404(report_id)
    
    if report.patient_id != current_user.id:
        flash('🔒 Unauthorized access', 'danger')
        return redirect(url_for('patient.patient_dashboard'))
    
    # جلب معلومات الطبيب إذا وجد
    doctor = None
    if report.doctor_id:
        doctor = Doctor.query.get(report.doctor_id)
    
    # جلب الوصفات المرتبطة (إذا كانت موجودة)
    related_prescriptions = Prescription.query.filter_by(
        patient_id=current_user.id
    ).order_by(Prescription.created_at.desc()).limit(3).all()
    
    return render_template('report/view_report.html',
                         show_header=True,
                         report=report,
                         doctor=doctor,
                         related_prescriptions=related_prescriptions,
                         datetime=datetime)


@patient_bp.route('/prescriptions')
@login_required
def patient_prescriptions():
    """عرض جميع الوصفات الطبية للمريض"""
    if session.get('user_role') != 'patient':
        flash('🔒 Unauthorized access', 'danger')
        return redirect(url_for('home'))
    
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id)\
                     .order_by(Prescription.created_at.desc()).all()
    
    # إحصائيات الوصفات
    active_count = sum(1 for p in prescriptions if p.is_active)
    expired_count = sum(1 for p in prescriptions if not p.is_active)
    
    return render_template('patient/patient_prescriptions.html',
                         show_header=True,
                         prescriptions=prescriptions,
                         active_count=active_count,
                         expired_count=expired_count,
                         datetime=datetime)


@patient_bp.route('/prescription/<int:prescription_id>/view')
@login_required
def view_prescription(prescription_id):
    """عرض تفاصيل وصفة طبية"""
    prescription = Prescription.query.get_or_404(prescription_id)
    
    if prescription.patient_id != current_user.id:
        flash('🔒 Unauthorized access', 'danger')
        return redirect(url_for('patient.patient_dashboard'))
    
    doctor = Doctor.query.get(prescription.doctor_id)
    
    return render_template('patient/view_prescription.html',
                         show_header=True,
                         prescription=prescription,
                         doctor=doctor,
                         datetime=datetime)


@patient_bp.route('/doctors')
@login_required
def patient_doctors():
    """عرض قائمة أطباء المريض"""
    if session.get('user_role') != 'patient':
        flash('🔒 Unauthorized access', 'danger')
        return redirect(url_for('home'))
    
    doctors = get_patient_doctors(current_user)
    
    # إحصائيات لكل طبيب
    doctors_data = []
    for doctor in doctors:
        reports_count = MedicalReport.query.filter_by(
            patient_id=current_user.id, 
            doctor_id=doctor.id
        ).count()
        
        prescriptions_count = Prescription.query.filter_by(
            patient_id=current_user.id,
            doctor_id=doctor.id
        ).count()
        
        doctors_data.append({
            'doctor': doctor,
            'reports_count': reports_count,
            'prescriptions_count': prescriptions_count
        })
    
    return render_template('patient/patient_doctors.html',
                         show_header=True,
                         doctors=doctors_data,
                         datetime=datetime)


@patient_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """تعديل الملف الشخصي للمريض"""
    if session.get('user_role') != 'patient':
        flash('🔒 Unauthorized access', 'danger')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        try:
            # تحديث المعلومات الأساسية
            current_user.name = request.form.get('name', current_user.name)
            current_user.phone = request.form.get('phone', current_user.phone)
            current_user.email = request.form.get('email', current_user.email) or None
            
            # تحديث المعلومات الطبية
            current_user.blood_type = request.form.get('blood_type', current_user.blood_type)
            current_user.allergies = request.form.get('allergies', current_user.allergies)
            current_user.chronic_conditions = request.form.get('chronic_conditions', current_user.chronic_conditions)
            current_user.current_medications = request.form.get('current_medications', current_user.current_medications)
            
            # معلومات الطوارئ
            current_user.emergency_contact_name = request.form.get('emergency_contact_name', current_user.emergency_contact_name)
            current_user.emergency_contact_phone = request.form.get('emergency_contact_phone', current_user.emergency_contact_phone)
            current_user.emergency_contact_relation = request.form.get('emergency_contact_relation', current_user.emergency_contact_relation)
            
            db.session.commit()
            flash('✅ Profile updated successfully', 'success')
            return redirect(url_for('patient.patient_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating profile: {e}")
            flash(f'❌ Error updating profile: {str(e)}', 'danger')
    
    return render_template('patient/edit_profile.html',
                         show_header=True,
                         patient=current_user)


# ===== API Endpoints للمريض =====

@patient_bp.route('/api/stats')
@login_required
def api_get_stats():
    """API لإحصائيات المريض"""
    if session.get('user_role') != 'patient':
        return jsonify({'error': 'Unauthorized'}), 403
    
    stats = get_patient_stats(current_user.id)
    
    return jsonify({
        'reports_count': stats['reports_count'],
        'prescriptions_count': stats['prescriptions_count'],
        'doctors_count': stats['doctors_count'],
        'alerts_count': stats['alerts_count'],
        'latest_report_date': stats['latest_report_date'].isoformat() if stats['latest_report_date'] else None
    })


@patient_bp.route('/api/reports')
@login_required
def api_get_reports():
    """API لجلب تقارير المريض (للاستخدام مع JavaScript)"""
    if session.get('user_role') != 'patient':
        return jsonify({'error': 'Unauthorized'}), 403
    
    reports = MedicalReport.query.filter_by(patient_id=current_user.id)\
                .order_by(MedicalReport.report_date.desc()).all()
    
    reports_data = [{
        'id': r.id,
        'date': r.report_date.isoformat(),
        'conditions': r.get_conditions(),
        'medications': r.get_medications(),
        'alerts': r.get_alerts(),
        'summary': r.summary[:200] + '...' if r.summary and len(r.summary) > 200 else r.summary
    } for r in reports]
    
    return jsonify({'reports': reports_data})


@patient_bp.route('/api/conditions')
@login_required
def api_get_conditions():
    """API لجلب جميع الحالات الطبية للمريض"""
    if session.get('user_role') != 'patient':
        return jsonify({'error': 'Unauthorized'}), 403
    
    reports = MedicalReport.query.filter_by(patient_id=current_user.id).all()
    
    all_conditions = set()
    for report in reports:
        conditions = report.get_conditions()
        for condition in conditions:
            if isinstance(condition, dict):
                all_conditions.add(condition.get('name', str(condition)))
            else:
                all_conditions.add(str(condition))
    
    return jsonify({'conditions': list(all_conditions)})


@patient_bp.route('/api/prescriptions')
@login_required
def api_get_prescriptions():
    """API لجلب الوصفات الطبية للمريض"""
    if session.get('user_role') != 'patient':
        return jsonify({'error': 'Unauthorized'}), 403
    
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id)\
                     .order_by(Prescription.created_at.desc()).all()
    
    prescriptions_data = [{
        'id': p.id,
        'date': p.created_at.isoformat(),
        'diagnosis': p.diagnosis,
        'is_active': p.is_active,
        'items_count': len(p.items),
        'doctor_name': p.doctor.name if p.doctor else None
    } for p in prescriptions]
    
    return jsonify({'prescriptions': prescriptions_data})