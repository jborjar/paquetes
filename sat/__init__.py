"""
Paquete SAT - Facturación Electrónica CFDI para México.

Este paquete proporciona herramientas completas para trabajar con CFDI (Comprobante
Fiscal Digital por Internet) y servicios del SAT (Servicio de Administración Tributaria).

Funcionalidades:
- Generación de CFDI 4.0 (Ingreso, Egreso, Pago, Nómina)
- Validación de estructura y sellos digitales
- Timbrado con PACs (Proveedores Autorizados de Certificación)
- Descarga masiva desde el portal del SAT
- Validación de RFCs y listas negras (69-B)
- Constancia de Situación Fiscal (CSF)

Instalación de dependencias:
    pip install satcfdi requests zeep pdfplumber

Variables de entorno opcionales:
    # Emisor
    SAT_EMISOR_RFC
    SAT_EMISOR_NOMBRE
    SAT_CERTIFICADO_PATH
    SAT_KEY_PATH
    SAT_KEY_PASSWORD

    # PAC (Proveedor de Timbrado)
    SAT_PAC_PROVIDER
    SAT_PAC_USERNAME
    SAT_PAC_PASSWORD
    SAT_PAC_MODE

    # FIEL (para descarga masiva y CSF)
    SAT_FIEL_CER
    SAT_FIEL_KEY
    SAT_FIEL_PASSWORD
"""

# Generación de CFDI
from .cfdi_generator import (
    create_cfdi_ingreso,
    create_cfdi_egreso,
    create_cfdi_pago,
    create_cfdi_nomina,
    xml_to_dict
)

# Validación de CFDI
from .cfdi_validator import (
    validate_cfdi_structure,
    validate_digital_seal,
    validate_cfdi_with_sat,
    extract_cfdi_data,
    validate_rfc_format as validate_rfc_format_validator
)

# Timbrado con PAC
from .cfdi_stamping import (
    stamp_cfdi,
    cancel_cfdi,
    get_stamp_status
)

# Descarga masiva SAT
from .sat_download import (
    request_download,
    check_download_status,
    download_packages,
    extract_packages,
    download_cfdi_full_process
)

# Validación de RFC y listas negras
from .rfc_validator import (
    validate_rfc_format,
    check_rfc_in_blacklist_69b,
    check_rfc_status_in_sat,
    check_multiple_rfcs,
    download_blacklist_69b,
    is_rfc_safe_to_transact
)

# Constancia de Situación Fiscal
from .csf import (
    get_csf,
    parse_csf_pdf,
    validate_csf,
    get_fiscal_situation_summary
)

# Validador de CSF
from .csf_validator import (
    validate_csf_from_pdf,
    generate_html_report,
    validate_csf_full
)


__all__ = [
    # Generación (5 funciones)
    'create_cfdi_ingreso',
    'create_cfdi_egreso',
    'create_cfdi_pago',
    'create_cfdi_nomina',
    'xml_to_dict',

    # Validación (5 funciones)
    'validate_cfdi_structure',
    'validate_digital_seal',
    'validate_cfdi_with_sat',
    'extract_cfdi_data',
    'validate_rfc_format_validator',

    # Timbrado (3 funciones)
    'stamp_cfdi',
    'cancel_cfdi',
    'get_stamp_status',

    # Descarga masiva (5 funciones)
    'request_download',
    'check_download_status',
    'download_packages',
    'extract_packages',
    'download_cfdi_full_process',

    # RFC y listas (6 funciones)
    'validate_rfc_format',
    'check_rfc_in_blacklist_69b',
    'check_rfc_status_in_sat',
    'check_multiple_rfcs',
    'download_blacklist_69b',
    'is_rfc_safe_to_transact',

    # CSF (4 funciones)
    'get_csf',
    'parse_csf_pdf',
    'validate_csf',
    'get_fiscal_situation_summary',

    # Validador CSF (3 funciones)
    'validate_csf_from_pdf',
    'generate_html_report',
    'validate_csf_full',
]

# Total: 31 funciones exportadas
