from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session, send_from_directory, current_app
from flask_login import login_required, current_user
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename

from backend.database import db, MedicalReport, Patient, Doctor
from backend.ocr_engine import extract_text
from backend.extensions import db

report_bp = Blueprint('report', __name__, url_prefix='/report')

# تكوين مجلد الرفع
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    """التحقق من امتداد الملف المسموح به"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@report_bp.route('/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id):
    """حذف تقرير (للمريض أو الطبيب)"""
    report = MedicalReport.query.get_or_404(report_id)
    user_role = session.get('user_role')
    
    current_app.logger.info(f"Delete attempt - User role: {user_role}, Report ID: {report_id}")
    
    # التحقق من الصلاحية حسب نوع المستخدم
    if user_role == 'patient':
        # المريض: يمكنه حذف تقاريره فقط
        if report.patient_id != current_user.id:
            flash('🔒 You don\'t have permission to delete this report', 'danger')
            return redirect(url_for('patient.patient_dashboard'))
        
        try:
            # حذف الصور المرتبطة بالتقرير
            image_paths = report.get_image_paths()
            for img_path in image_paths:
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, img_path))
                except:
                    pass
            
            db.session.delete(report)
            db.session.commit()
            flash('✅ Report deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting report: {e}")
            flash(f'❌ Error deleting report: {str(e)}', 'danger')
        
        return redirect(url_for('patient.patient_dashboard'))
        
    elif user_role == 'doctor':
        # الطبيب: يمكنه حذف تقارير مرضاه فقط
        patient = Patient.query.get(report.patient_id)
        
        if not patient or current_user not in patient.doctors:
            flash('🔒 You don\'t have permission to delete this report', 'danger')
            return redirect(url_for('doctor.doctor_dashboard'))
        
        try:
            # حذف الصور المرتبطة بالتقرير
            image_paths = report.get_image_paths()
            for img_path in image_paths:
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, img_path))
                except:
                    pass
            
            db.session.delete(report)
            db.session.commit()
            flash('✅ Report deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting report: {e}")
            flash(f'❌ Error deleting report: {str(e)}', 'danger')
        
        return redirect(url_for('doctor.patient_reports', patient_id=report.patient_id))
        
    else:
        flash('🔒 Unauthorized access', 'danger')
        return redirect(url_for('home'))


@report_bp.route('/ocr', methods=['POST'])
@login_required
def ocr():
    """استخراج النص من الصورة باستخدام Tesseract OCR"""
    try:
        # التحقق من وجود ملف
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        
        # التحقق من امتداد الملف
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed. Use PNG, JPG, JPEG, GIF, or PDF"}), 400
        
        # حفظ الملف
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = secure_filename(f"{timestamp}_{file.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        current_app.logger.info(f"OCR - File saved: {file_path}")
        
        # استخراج النص
        text = extract_text(file_path)
        
        current_app.logger.info(f"OCR - Text extracted, length: {len(text)} characters")
        
        return jsonify({
            "success": True,
            "text": text,
            "image_path": filename
        })
        
    except Exception as e:
        current_app.logger.error(f"OCR Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@report_bp.route('/save-report', methods=['POST'])
@login_required
def save_report():
    """حفظ التقرير بعد تحليل الذكاء الاصطناعي"""
    try:
        data = request.json
        
        # التحقق من البيانات المطلوبة
        if not data.get('patient_id'):
            return jsonify({"error": "Patient ID is required"}), 400
        
        patient_id = data.get('patient_id')
        
        # التحقق من صلاحية الوصول للمريض
        user_role = session.get('user_role')
        if user_role == 'doctor':
            patient = Patient.query.get(patient_id)
            if not patient or current_user not in patient.doctors:
                return jsonify({"error": "Unauthorized access to this patient"}), 403
        elif user_role == 'patient':
            if current_user.id != patient_id:
                return jsonify({"error": "Unauthorized access"}), 403
        else:
            return jsonify({"error": "Unauthorized"}), 403
        
        # إنشاء التقرير
        report = MedicalReport(
            patient_id=patient_id,
            doctor_id=current_user.id if user_role == 'doctor' else None,
            conditions=json.dumps(data.get('conditions', [])),
            medications=json.dumps(data.get('medications', [])),
            alerts=json.dumps(data.get('alerts', [])),
            summary=data.get('summary', '')
        )
        
        # إضافة مسارات الصور
        image_paths = data.get('image_paths', [])
        report.set_image_paths(image_paths)
        
        db.session.add(report)
        db.session.commit()
        
        current_app.logger.info(f"Report saved - ID: {report.id}, Patient: {patient_id}")
        
        return jsonify({
            "success": True,
            "id": report.id,
            "message": "Report saved successfully"
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Save report error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@report_bp.route('/<int:report_id>/edit', methods=['POST'])
@login_required
def edit_report(report_id):
    """تعديل تقرير موجود"""
    try:
        report = MedicalReport.query.get_or_404(report_id)
        user_role = session.get('user_role')
        
        # التحقق من الصلاحية
        if user_role == 'patient' and report.patient_id != current_user.id:
            return jsonify({"error": "Unauthorized"}), 403
        elif user_role == 'doctor':
            patient = Patient.query.get(report.patient_id)
            if not patient or current_user not in patient.doctors:
                return jsonify({"error": "Unauthorized"}), 403
        
        data = request.json
        
        # تحديث الحقول
        if 'conditions' in data:
            report.conditions = json.dumps(data['conditions'])
        if 'medications' in data:
            report.medications = json.dumps(data['medications'])
        if 'alerts' in data:
            report.alerts = json.dumps(data['alerts'])
        if 'summary' in data:
            report.summary = data['summary']
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Report updated successfully"
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Edit report error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@report_bp.route('/<int:report_id>/export')
@login_required
def export_report(report_id):
    """تصدير التقرير بتنسيق JSON"""
    report = MedicalReport.query.get_or_404(report_id)
    user_role = session.get('user_role')
    
    # التحقق من الصلاحية
    if user_role == 'patient' and report.patient_id != current_user.id:
        flash('🔒 Unauthorized access', 'danger')
        return redirect(url_for('patient.patient_dashboard'))
    elif user_role == 'doctor':
        patient = Patient.query.get(report.patient_id)
        if not patient or current_user not in patient.doctors:
            flash('🔒 Unauthorized access', 'danger')
            return redirect(url_for('doctor.doctor_dashboard'))
    
    # تجهيز بيانات التصدير
    export_data = {
        'id': report.id,
        'patient_id': report.patient_id,
        'doctor_id': report.doctor_id,
        'report_date': report.report_date.isoformat(),
        'conditions': report.get_conditions(),
        'medications': report.get_medications(),
        'alerts': report.get_alerts(),
        'summary': report.summary,
        'image_paths': report.get_image_paths()
    }
    
    return jsonify(export_data)


# ===== مسارات إضافية =====

@report_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """عرض الصورة المرفوعة"""
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    return send_from_directory(uploads_dir, filename)


@report_bp.route('/patient/<int:patient_id>/reports')
@login_required
def get_patient_reports(patient_id):
    """API لجلب تقارير المريض (للاستخدام مع JavaScript)"""
    user_role = session.get('user_role')
    
    # التحقق من الصلاحية
    if user_role == 'doctor':
        patient = Patient.query.get(patient_id)
        if not patient or current_user not in patient.doctors:
            return jsonify({"error": "Unauthorized"}), 403
    elif user_role == 'patient':
        if current_user.id != patient_id:
            return jsonify({"error": "Unauthorized"}), 403
    else:
        return jsonify({"error": "Unauthorized"}), 403
    
    reports = MedicalReport.query.filter_by(patient_id=patient_id)\
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