"""
Validador de Constancias de Situación Fiscal (CSF) del SAT.

Este módulo proporciona funciones para validar PDFs de CSF y generar reportes HTML.
Es completamente portable y genérico, sin dependencias de configuración interna.

Funciones principales:
- validate_csf_from_pdf: Valida un PDF de CSF y retorna datos estructurados
- generate_html_report: Genera un reporte HTML profesional
- validate_csf_full: Proceso completo de validación con reporte HTML

Dependencias:
    pip install pdfplumber

Uso básico:
    from paquetes.sat.csf_validator import validate_csf_full

    result = validate_csf_full(
        pdf_file='constancia.pdf',
        expected_rfc='XAXX010101000',
        output_html='reporte.html'
    )

    if result['success']:
        print(f"Reporte generado: {result['html_file']}")
"""
import os
from typing import Dict, Optional, Any
from datetime import datetime
from pathlib import Path


def validate_csf_from_pdf(
    pdf_file: str,
    expected_rfc: Optional[str] = None
) -> Dict[str, Any]:
    """
    Valida un PDF de CSF y extrae información.

    Args:
        pdf_file: Ruta al archivo PDF de la CSF
        expected_rfc: RFC esperado (opcional, se puede extraer del PDF)

    Returns:
        Dict con datos de validación:
        {
            'success': bool,
            'rfc': str,
            'csf_rfc': str,
            'csf_nombre': str,
            'formato_valido': bool,
            'tipo_persona': str,
            'estado': str,
            'activo': bool,
            'seguro_transaccionar': bool,
            'regimenes': list,
            'riesgos': list,
            'csf_valida': bool,
            'csf_errores': list,
            'csf_warnings': list
        }

    Example:
        >>> data = validate_csf_from_pdf('constancia.pdf', 'XAXX010101000')
        >>> if data['success']:
        ...     print(f"RFC: {data['rfc']}")
        ...     print(f"Estado: {data['estado']}")
        ...     print(f"Seguro transaccionar: {data['seguro_transaccionar']}")
    """
    try:
        from paquetes.sat import (
            parse_csf_pdf,
            validate_csf,
            get_fiscal_situation_summary,
            validate_rfc_format,
            is_rfc_safe_to_transact
        )
    except ImportError as e:
        return {
            'success': False,
            'error': f'Error al importar módulo SAT: {e}'
        }

    resultado = {
        'success': False,
        'fecha_validacion': datetime.now().isoformat(),
        'archivo_pdf': pdf_file,
        'formato_valido': False,
        'rfc': expected_rfc or 'Desconocido'
    }

    # Verificar que el archivo existe
    if not os.path.exists(pdf_file):
        resultado['error'] = f'Archivo no encontrado: {pdf_file}'
        return resultado

    # Paso 1: Extraer datos del PDF
    csf_datos = parse_csf_pdf(pdf_file)
    if not csf_datos['success']:
        resultado['error'] = f"Error al leer PDF: {csf_datos['error']}"
        return resultado

    # Obtener RFC del PDF o usar el esperado
    rfc = csf_datos.get('rfc') or expected_rfc
    if not rfc:
        resultado['error'] = 'RFC no encontrado en PDF ni proporcionado'
        return resultado

    resultado['rfc'] = rfc
    resultado['csf_rfc'] = csf_datos.get('rfc')
    resultado['csf_nombre'] = csf_datos.get('nombre')

    # Paso 2: Validar formato de RFC
    formato = validate_rfc_format(rfc)
    resultado['formato_valido'] = formato['valid']

    if not formato['valid']:
        resultado['error'] = f"RFC inválido: {formato['error']}"
        return resultado

    resultado['tipo_persona'] = formato['tipo']
    resultado['longitud'] = formato['longitud']

    # Paso 3: Obtener situación fiscal
    resumen = get_fiscal_situation_summary(rfc)
    if resumen['success']:
        resultado['estado'] = resumen['estado']
        resultado['activo'] = resumen['activo']
        resultado['nombre'] = resumen.get('nombre')
        resultado['regimenes'] = resumen.get('regimenes', [])
        resultado['riesgos'] = resumen.get('riesgos', [])

    # Paso 4: Validar para transacciones
    seguridad = is_rfc_safe_to_transact(rfc)
    resultado['seguro_transaccionar'] = seguridad['seguro']

    # Paso 5: Validar la CSF
    validacion_csf = validate_csf(
        rfc=rfc,
        csf_data=csf_datos,
        fecha_emision=None
    )

    resultado['csf_valida'] = validacion_csf['valid']
    resultado['csf_errores'] = validacion_csf.get('errors', [])
    resultado['csf_warnings'] = validacion_csf.get('warnings', [])

    resultado['success'] = True
    return resultado


def generate_html_report(
    validation_data: Dict[str, Any],
    output_file: str
) -> Dict[str, Any]:
    """
    Genera un reporte HTML profesional a partir de los datos de validación.

    Args:
        validation_data: Diccionario retornado por validate_csf_from_pdf()
        output_file: Ruta del archivo HTML de salida

    Returns:
        Dict con resultado:
        {
            'success': bool,
            'html_file': str,
            'size_bytes': int
        }

    Example:
        >>> data = validate_csf_from_pdf('constancia.pdf')
        >>> result = generate_html_report(data, 'reporte.html')
        >>> print(f"Reporte: {result['html_file']}")
    """
    try:
        datos = validation_data

        # Construir secciones HTML dinámicas
        seccion_csf = ""
        if datos.get('csf_rfc'):
            archivo_info = f'<div style="margin-top: 20px;"><strong>Archivo PDF:</strong><br>{datos.get("archivo_pdf")}</div>' if datos.get('archivo_pdf') else ''
            seccion_csf = f'''
                <div class="seccion">
                    <h2>4. Datos Extraídos de la CSF</h2>
                    <div class="card">
                        <div class="info-grid">
                            <div class="info-item">
                                <div class="label">RFC en CSF</div>
                                <div class="value">{datos.get('csf_rfc', 'N/A')}</div>
                            </div>
                            <div class="info-item">
                                <div class="label">Nombre en CSF</div>
                                <div class="value">{datos.get('csf_nombre', 'N/A')}</div>
                            </div>
                        </div>
                        {archivo_info}
                    </div>
                </div>'''

        # Sección de validación CSF
        seccion_validacion_csf = ""
        if datos.get('csf_valida') is not None:
            badge_class = 'badge-success' if datos.get('csf_valida') else 'badge-danger'
            badge_text = '✓ CSF Válida' if datos.get('csf_valida') else '✗ CSF Inválida'

            errores_html = ""
            if datos.get('csf_errores'):
                errores_items = ''.join([f'<li>{error}</li>' for error in datos['csf_errores']])
                errores_html = f'<div style="margin-top: 15px;"><strong>Errores:</strong><ul class="lista errores">{errores_items}</ul></div>'

            warnings_html = ""
            if datos.get('csf_warnings'):
                warnings_items = ''.join([f'<li>{warning}</li>' for warning in datos['csf_warnings']])
                warnings_html = f'<div style="margin-top: 15px;"><strong>Advertencias:</strong><ul class="lista riesgos">{warnings_items}</ul></div>'

            seccion_validacion_csf = f'''
                <div class="seccion">
                    <h2>5. Validación de la CSF</h2>
                    <div class="card">
                        <span class="status-badge {badge_class}">{badge_text}</span>
                        {errores_html}
                        {warnings_html}
                    </div>
                </div>'''

        # Sección de regímenes
        regimenes_html = ""
        if datos.get('regimenes'):
            regimenes_items = ''.join([f'<li>{reg}</li>' for reg in datos['regimenes']])
            regimenes_html = f'<div style="margin-top: 20px;"><strong>Regímenes Fiscales:</strong><ul class="lista">{regimenes_items}</ul></div>'

        # Sección de riesgos
        riesgos_html = ""
        if datos.get('riesgos'):
            riesgos_items = ''.join([f'<li>{riesgo}</li>' for riesgo in datos['riesgos']])
            riesgos_html = f'<div style="margin-top: 15px;"><strong>Riesgos:</strong><ul class="lista riesgos">{riesgos_items}</ul></div>'
        else:
            riesgos_html = '<p style="margin-top: 15px; color: #28a745;">✓ Sin riesgos detectados</p>'

        # Resumen de riesgos
        resumen_riesgos = ""
        if datos.get('riesgos'):
            riesgos_lista = '<br>'.join([f'• {r}' for r in datos['riesgos']])
            resumen_riesgos = f'<div style="margin-top: 20px; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 6px;"><strong>⚠ Riesgos:</strong><br>{riesgos_lista}</div>'
        else:
            resumen_riesgos = '<div style="margin-top: 20px; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 6px;">✓ Sin riesgos - Seguro para transacciones</div>'

        # Nombre opcional
        nombre_html = ""
        if datos.get('nombre'):
            nombre_html = f'<div class="info-item"><div class="label">Nombre / Razón Social</div><div class="value">{datos["nombre"]}</div></div>'

        # Generar HTML completo
        html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte CSF - {datos['rfc']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .header .rfc {{ font-size: 1.5em; font-weight: bold; letter-spacing: 2px; margin: 15px 0; }}
        .header .fecha {{ opacity: 0.9; font-size: 0.9em; }}
        .content {{ padding: 30px; }}
        .seccion {{ margin-bottom: 30px; border-left: 4px solid #667eea; padding-left: 20px; }}
        .seccion h2 {{ color: #667eea; margin-bottom: 15px; font-size: 1.5em; }}
        .card {{ background: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 15px; }}
        .status-badge {{ display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: bold; font-size: 0.9em; margin: 10px 0; }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-warning {{ background: #fff3cd; color: #856404; }}
        .badge-danger {{ background: #f8d7da; color: #721c24; }}
        .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 15px; }}
        .info-item {{ background: white; padding: 15px; border-radius: 6px; border-left: 3px solid #667eea; }}
        .info-item .label {{ font-size: 0.85em; color: #666; margin-bottom: 5px; text-transform: uppercase; font-weight: 600; }}
        .info-item .value {{ font-size: 1.1em; color: #333; font-weight: 500; }}
        .lista {{ list-style: none; margin-top: 10px; }}
        .lista li {{ padding: 8px 0; border-bottom: 1px solid #eee; }}
        .lista li:before {{ content: "✓ "; color: #28a745; font-weight: bold; margin-right: 8px; }}
        .lista.riesgos li:before {{ content: "⚠ "; color: #ffc107; }}
        .lista.errores li:before {{ content: "✗ "; color: #dc3545; }}
        .resumen {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 8px; margin-top: 30px; }}
        .resumen h3 {{ margin-bottom: 15px; font-size: 1.3em; }}
        .resumen-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px; }}
        .resumen-item {{ background: rgba(255,255,255,0.1); padding: 15px; border-radius: 6px; }}
        .resumen-item .label {{ font-size: 0.85em; opacity: 0.9; margin-bottom: 5px; }}
        .resumen-item .value {{ font-size: 1.3em; font-weight: bold; }}
        .footer {{ text-align: center; padding: 20px; background: #f8f9fa; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Reporte de Validación CSF</h1>
            <div class="rfc">{datos['rfc']}</div>
            <div class="fecha">Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        <div class="content">
            <div class="seccion">
                <h2>1. Validación de RFC</h2>
                <div class="card">
                    <span class="status-badge {'badge-success' if datos['formato_valido'] else 'badge-danger'}">
                        {'✓ RFC Válido' if datos['formato_valido'] else '✗ RFC Inválido'}
                    </span>
                    <div class="info-grid">
                        <div class="info-item"><div class="label">RFC</div><div class="value">{datos['rfc']}</div></div>
                        <div class="info-item"><div class="label">Tipo</div><div class="value">{datos.get('tipo_persona', 'N/A')}</div></div>
                        <div class="info-item"><div class="label">Longitud</div><div class="value">{datos.get('longitud', 'N/A')} caracteres</div></div>
                    </div>
                </div>
            </div>
            <div class="seccion">
                <h2>2. Situación Fiscal</h2>
                <div class="card">
                    <span class="status-badge {'badge-success' if datos.get('activo') else 'badge-danger'}">
                        {datos.get('estado', 'Desconocido')}
                    </span>
                    <div class="info-grid">
                        {nombre_html}
                        <div class="info-item"><div class="label">Contribuyente</div><div class="value">{'Activo' if datos.get('activo') else 'Inactivo'}</div></div>
                    </div>
                    {regimenes_html}
                </div>
            </div>
            <div class="seccion">
                <h2>3. Validación para Transacciones</h2>
                <div class="card">
                    <span class="status-badge {'badge-success' if datos.get('seguro_transaccionar') else 'badge-warning'}">
                        {'✓ Aprobado' if datos.get('seguro_transaccionar') else '⚠ Con Riesgos'}
                    </span>
                    {riesgos_html}
                </div>
            </div>
            {seccion_csf}
            {seccion_validacion_csf}
            <div class="resumen">
                <h3>📊 Resumen Final</h3>
                <div class="resumen-grid">
                    <div class="resumen-item"><div class="label">RFC</div><div class="value">{datos['rfc']}</div></div>
                    <div class="resumen-item"><div class="label">Tipo</div><div class="value">{datos.get('tipo_persona', 'N/A')}</div></div>
                    <div class="resumen-item"><div class="label">Estado</div><div class="value">{datos.get('estado', 'Desconocido')}</div></div>
                    <div class="resumen-item"><div class="label">Transacciones</div><div class="value">{'✓ Aprobado' if datos.get('seguro_transaccionar') else '⚠ Riesgos'}</div></div>
                </div>
                {resumen_riesgos}
            </div>
        </div>
        <div class="footer">
            <p>Reporte generado por Sistema de Validación CSF</p>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>'''

        # Guardar HTML
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        file_size = os.path.getsize(output_file)

        return {
            'success': True,
            'html_file': output_file,
            'size_bytes': file_size
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def validate_csf_full(
    pdf_file: str,
    expected_rfc: Optional[str] = None,
    output_html: Optional[str] = None
) -> Dict[str, Any]:
    """
    Proceso completo de validación CSF con generación de reporte HTML.

    Esta función realiza:
    1. Validación del PDF de CSF
    2. Consulta de situación fiscal en el SAT
    3. Verificación de listas negras
    4. Generación de reporte HTML (opcional)

    Args:
        pdf_file: Ruta al archivo PDF de la CSF
        expected_rfc: RFC esperado (opcional)
        output_html: Ruta del archivo HTML de salida (opcional)
                    Si no se especifica, se genera automáticamente

    Returns:
        Dict con resultado completo:
        {
            'success': bool,
            'validation_data': dict,
            'html_file': str (si output_html se especificó),
            'error': str (si falló)
        }

    Example:
        >>> # Validación simple sin HTML
        >>> result = validate_csf_full('constancia.pdf')
        >>> print(result['validation_data']['seguro_transaccionar'])
        >>>
        >>> # Validación completa con reporte HTML
        >>> result = validate_csf_full(
        ...     pdf_file='constancia.pdf',
        ...     expected_rfc='XAXX010101000',
        ...     output_html='reporte.html'
        ... )
        >>> if result['success']:
        ...     print(f"Reporte: {result['html_file']}")
    """
    # Validar CSF
    validation_data = validate_csf_from_pdf(pdf_file, expected_rfc)

    if not validation_data['success']:
        return {
            'success': False,
            'error': validation_data.get('error', 'Error desconocido'),
            'validation_data': validation_data
        }

    resultado = {
        'success': True,
        'validation_data': validation_data
    }

    # Generar HTML si se solicita
    if output_html or output_html is None:
        if output_html is None:
            # Generar nombre automático
            rfc = validation_data['rfc']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_html = f"reporte_csf_{rfc}_{timestamp}.html"

        html_result = generate_html_report(validation_data, output_html)

        if html_result['success']:
            resultado['html_file'] = html_result['html_file']
            resultado['html_size_bytes'] = html_result['size_bytes']
        else:
            resultado['html_error'] = html_result.get('error')

    return resultado


# Alias para compatibilidad
validate_csf = validate_csf_full
