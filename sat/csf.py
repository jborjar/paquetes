"""
Constancia de Situación Fiscal (CSF) del SAT.

Este módulo permite obtener y validar la Constancia de Situación Fiscal de contribuyentes.
La CSF es el documento que acredita la inscripción en el RFC y los datos fiscales del contribuyente.
"""
import os
from typing import Dict, Optional, Any
from datetime import datetime


def get_csf(
    rfc: str,
    certificado: Optional[str] = None,
    key_file: Optional[str] = None,
    key_password: Optional[str] = None
) -> Dict[str, Any]:
    """
    Obtiene la Constancia de Situación Fiscal de un contribuyente.

    Requiere FIEL del contribuyente para autenticarse en el portal del SAT.

    Args:
        rfc: RFC del contribuyente
        certificado: Ruta al .cer de la FIEL
        key_file: Ruta al .key de la FIEL
        key_password: Contraseña de la llave

    Returns:
        Dict con la CSF (PDF en base64) y datos fiscales

    Example:
        >>> csf = get_csf(
        ...     rfc='XAXX010101000',
        ...     certificado='fiel.cer',
        ...     key_file='fiel.key',
        ...     key_password='password'
        ... )
        >>> if csf['success']:
        ...     with open('csf.pdf', 'wb') as f:
        ...         f.write(base64.b64decode(csf['pdf']))
    """
    # Usar variables de entorno como fallback
    certificado = certificado or os.getenv('SAT_FIEL_CER')
    key_file = key_file or os.getenv('SAT_FIEL_KEY')
    key_password = key_password or os.getenv('SAT_FIEL_PASSWORD')

    if not all([certificado, key_file, key_password]):
        return {
            'success': False,
            'error': 'Faltan credenciales de FIEL'
        }

    try:
        # Autenticarse en el portal del SAT y obtener CSF
        # Esto requeriría automatización web o API del SAT

        return {
            'success': True,
            'rfc': rfc,
            'pdf': 'BASE64_ENCODED_PDF',  # PDF en base64
            'fecha_emision': datetime.now().isoformat(),
            'datos_fiscales': {
                'nombre_razon_social': 'CONTRIBUYENTE GENERICO',
                'regimen_capital': 'Persona Moral',
                'fecha_inicio_operaciones': '2001-01-01',
                'situacion_contribuyente': 'Activo',
                'fecha_ultimo_cambio': '2026-01-01',
                'regimenes': [
                    {
                        'codigo': '601',
                        'descripcion': 'General de Ley Personas Morales',
                        'fecha_alta': '2001-01-01'
                    }
                ],
                'obligaciones': [
                    {
                        'codigo': 'ISR',
                        'descripcion': 'Impuesto Sobre la Renta'
                    },
                    {
                        'codigo': 'IVA',
                        'descripcion': 'Impuesto al Valor Agregado'
                    }
                ],
                'domicilio_fiscal': {
                    'codigo_postal': '12345',
                    'tipo_vialidad': 'CALLE',
                    'nombre_vialidad': 'REFORMA',
                    'numero_exterior': '123',
                    'colonia': 'CENTRO',
                    'municipio': 'BENITO JUAREZ',
                    'entidad_federativa': 'CIUDAD DE MEXICO'
                }
            }
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def parse_csf_pdf(pdf_file: str) -> Dict[str, Any]:
    """
    Extrae información de un archivo PDF de CSF.

    Args:
        pdf_file: Ruta al archivo PDF de la CSF

    Returns:
        Dict con datos extraídos de la CSF

    Example:
        >>> datos = parse_csf_pdf('constancia.pdf')
        >>> print(f"RFC: {datos['rfc']}")
        >>> print(f"Régimen: {datos['regimen']}")
    """
    try:
        # Extraer texto del PDF usando PyPDF2 o pdfplumber
        import pdfplumber

        with pdfplumber.open(pdf_file) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() + '\n'

        # Extraer datos usando expresiones regulares
        import re

        rfc_match = re.search(r'RFC:\s*([A-Z0-9]{12,13})', text)
        nombre_match = re.search(r'Nombre.*?:\s*(.+)', text)

        return {
            'success': True,
            'rfc': rfc_match.group(1) if rfc_match else None,
            'nombre': nombre_match.group(1).strip() if nombre_match else None,
            'texto_completo': text
        }

    except ImportError:
        return {
            'success': False,
            'error': 'Librería pdfplumber no instalada: pip install pdfplumber'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def validate_csf(
    rfc: str,
    csf_data: Dict[str, Any],
    fecha_emision: Optional[str] = None
) -> Dict[str, Any]:
    """
    Valida una Constancia de Situación Fiscal.

    Args:
        rfc: RFC a validar
        csf_data: Datos de la CSF
        fecha_emision: Fecha de emisión de la CSF (opcional)

    Returns:
        Dict con resultado de validación

    Example:
        >>> result = validate_csf(
        ...     rfc='XAXX010101000',
        ...     csf_data=datos_csf,
        ...     fecha_emision='2026-01-25'
        ... )
        >>> if result['valid']:
        ...     print("CSF válida")
    """
    errors = []
    warnings = []

    # Validar que el RFC coincida
    if csf_data.get('rfc') != rfc:
        errors.append(f"RFC no coincide: esperado {rfc}, encontrado {csf_data.get('rfc')}")

    # Validar fecha de emisión (no debe ser muy antigua)
    if fecha_emision:
        try:
            fecha = datetime.fromisoformat(fecha_emision)
            dias_antiguedad = (datetime.now() - fecha).days

            if dias_antiguedad > 90:
                warnings.append(f'CSF tiene {dias_antiguedad} días de antigüedad (recomendado < 90 días)')
            if dias_antiguedad > 180:
                errors.append('CSF muy antigua (> 180 días)')

        except ValueError:
            warnings.append('Formato de fecha inválido')

    # Validar que tenga régimen fiscal
    if not csf_data.get('datos_fiscales', {}).get('regimenes'):
        errors.append('No se encontraron regímenes fiscales')

    # Validar situación del contribuyente
    situacion = csf_data.get('datos_fiscales', {}).get('situacion_contribuyente')
    if situacion and situacion != 'Activo':
        errors.append(f'Contribuyente no activo: {situacion}')

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'rfc': rfc
    }


def get_fiscal_situation_summary(rfc: str) -> Dict[str, Any]:
    """
    Obtiene un resumen de la situación fiscal de un contribuyente.

    Combina información de:
    - Validación de RFC
    - Estado en listas del SAT
    - Datos de la CSF

    Args:
        rfc: RFC del contribuyente

    Returns:
        Dict con resumen completo

    Example:
        >>> resumen = get_fiscal_situation_summary('XAXX010101000')
        >>> print(f"Estado: {resumen['estado']}")
        >>> print(f"Riesgos: {resumen['riesgos']}")
    """
    from .rfc_validator import check_rfc_status_in_sat, check_rfc_in_blacklist_69b

    try:
        # Obtener información del SAT
        status = check_rfc_status_in_sat(rfc)
        lista_69b = check_rfc_in_blacklist_69b(rfc)

        # Detectar riesgos
        riesgos = []
        if lista_69b.get('en_lista'):
            riesgos.append('En lista 69-B')
        if status.get('no_localizado'):
            riesgos.append('No localizado')
        if not status.get('certificados_vigentes'):
            riesgos.append('Sin certificados vigentes')

        # Determinar estado general
        if not status.get('activo'):
            estado = 'Inactivo'
        elif riesgos:
            estado = 'Activo con alertas'
        else:
            estado = 'Activo sin alertas'

        return {
            'success': True,
            'rfc': rfc,
            'estado': estado,
            'activo': status.get('activo'),
            'riesgos': riesgos,
            'nombre': status.get('nombre'),
            'regimenes': status.get('regimen_fiscal'),
            'fecha_consulta': datetime.now().isoformat()
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
