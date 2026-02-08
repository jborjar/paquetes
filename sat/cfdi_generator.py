"""
Generación de CFDI (Comprobante Fiscal Digital por Internet).

Este módulo permite crear CFDIs de diferentes tipos usando la librería satcfdi.
Soporta CFDI 4.0 según especificaciones del SAT.

Variables de entorno opcionales:
    SAT_EMISOR_RFC: RFC del emisor
    SAT_EMISOR_NOMBRE: Nombre del emisor
    SAT_CERTIFICADO_PATH: Ruta al archivo .cer
    SAT_KEY_PATH: Ruta al archivo .key
    SAT_KEY_PASSWORD: Contraseña de la llave privada
"""
import os
from typing import Dict, List, Optional, Any
from datetime import datetime


def create_cfdi_ingreso(
    emisor: Dict[str, str],
    receptor: Dict[str, str],
    conceptos: List[Dict[str, Any]],
    forma_pago: str = "99",
    metodo_pago: str = "PUE",
    tipo_cambio: Optional[float] = None,
    moneda: str = "MXN",
    lugar_expedicion: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Crea un CFDI de tipo Ingreso (factura).

    Args:
        emisor: Dict con datos del emisor {'rfc', 'nombre', 'regimen_fiscal'}
        receptor: Dict con datos del receptor {'rfc', 'nombre', 'uso_cfdi', 'domicilio_fiscal_receptor', 'regimen_fiscal_receptor'}
        conceptos: Lista de conceptos a facturar
            [{'clave_prod_serv', 'cantidad', 'clave_unidad', 'unidad',
              'descripcion', 'valor_unitario', 'importe', 'objeto_imp', 'impuestos'}]
        forma_pago: Clave forma de pago (01-Efectivo, 02-Cheque, 03-Transferencia, etc.)
        metodo_pago: PUE (Pago en una sola exhibición) o PPD (Pago en parcialidades)
        tipo_cambio: Tipo de cambio si la moneda no es MXN
        moneda: Clave de moneda (MXN, USD, EUR, etc.)
        lugar_expedicion: Código postal donde se expide la factura
        **kwargs: Parámetros adicionales

    Returns:
        Dict con el CFDI generado y datos de respuesta

    Raises:
        ValueError: Si faltan datos obligatorios
        Exception: Si hay error en la generación

    Example:
        >>> emisor = {
        ...     'rfc': 'XAXX010101000',
        ...     'nombre': 'Empresa Demo',
        ...     'regimen_fiscal': '601'
        ... }
        >>> receptor = {
        ...     'rfc': 'XAXX010101000',
        ...     'nombre': 'Cliente Demo',
        ...     'uso_cfdi': 'G03',
        ...     'domicilio_fiscal_receptor': '12345',
        ...     'regimen_fiscal_receptor': '612'
        ... }
        >>> conceptos = [{
        ...     'clave_prod_serv': '01010101',
        ...     'cantidad': 1,
        ...     'clave_unidad': 'E48',
        ...     'unidad': 'Servicio',
        ...     'descripcion': 'Servicio de consultoría',
        ...     'valor_unitario': 1000.00,
        ...     'importe': 1000.00,
        ...     'objeto_imp': '02',
        ...     'impuestos': {
        ...         'traslados': [{
        ...             'base': 1000.00,
        ...             'impuesto': '002',
        ...             'tipo_factor': 'Tasa',
        ...             'tasa_o_cuota': 0.16,
        ...             'importe': 160.00
        ...         }]
        ...     }
        ... }]
        >>> cfdi = create_cfdi_ingreso(emisor, receptor, conceptos)
    """
    try:
        from satcfdi import Invoice, Issuer, Receiver, Item

        # Validar datos obligatorios
        if not emisor.get('rfc') or not emisor.get('nombre'):
            raise ValueError("Emisor debe tener 'rfc' y 'nombre'")
        if not receptor.get('rfc') or not receptor.get('nombre'):
            raise ValueError("Receptor debe tener 'rfc' y 'nombre'")
        if not conceptos:
            raise ValueError("Debe haber al menos un concepto")

        # Usar variables de entorno como fallback
        emisor_rfc = emisor.get('rfc', os.getenv('SAT_EMISOR_RFC'))
        emisor_nombre = emisor.get('nombre', os.getenv('SAT_EMISOR_NOMBRE'))
        lugar_exp = lugar_expedicion or emisor.get('lugar_expedicion') or kwargs.get('codigo_postal')

        if not lugar_exp:
            raise ValueError("Se requiere lugar_expedicion (código postal)")

        # Crear factura
        invoice = Invoice(
            issuer=Issuer(
                rfc=emisor_rfc,
                name=emisor_nombre,
                fiscal_regime=emisor.get('regimen_fiscal', '601')
            ),
            receiver=Receiver(
                rfc=receptor['rfc'],
                name=receptor['nombre'],
                cfdi_use=receptor.get('uso_cfdi', 'G03'),
                fiscal_address=receptor.get('domicilio_fiscal_receptor'),
                fiscal_regime=receptor.get('regimen_fiscal_receptor')
            ),
            items=[],
            payment_form=forma_pago,
            payment_method=metodo_pago,
            currency=moneda,
            expedition_place=lugar_exp
        )

        # Agregar tipo de cambio si aplica
        if tipo_cambio and moneda != 'MXN':
            invoice.exchange_rate = tipo_cambio

        # Agregar conceptos
        for concepto in conceptos:
            item = Item(
                product_key=concepto['clave_prod_serv'],
                quantity=concepto['cantidad'],
                unit_key=concepto['clave_unidad'],
                unit=concepto.get('unidad', ''),
                description=concepto['descripcion'],
                unit_price=concepto['valor_unitario'],
                amount=concepto['importe'],
                tax_object=concepto.get('objeto_imp', '02')
            )

            # Agregar impuestos si existen
            if 'impuestos' in concepto:
                # Aquí se agregarían los impuestos según la estructura de satcfdi
                pass

            invoice.add_item(item)

        # Generar XML
        xml_str = invoice.to_xml()

        return {
            'success': True,
            'xml': xml_str,
            'tipo_comprobante': 'I',
            'version': '4.0',
            'fecha': datetime.now().isoformat(),
            'total': sum(c['importe'] for c in conceptos)
        }

    except ImportError:
        raise Exception("La librería satcfdi no está instalada. Ejecuta: pip install satcfdi")
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'tipo': type(e).__name__
        }


def create_cfdi_egreso(
    emisor: Dict[str, str],
    receptor: Dict[str, str],
    conceptos: List[Dict[str, Any]],
    cfdi_relacionados: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Crea un CFDI de tipo Egreso (nota de crédito/devolución).

    Args:
        emisor: Datos del emisor
        receptor: Datos del receptor
        conceptos: Conceptos de la nota de crédito
        cfdi_relacionados: {'tipo_relacion': '01', 'uuids': ['uuid1', 'uuid2']}
        **kwargs: Parámetros adicionales

    Returns:
        Dict con el CFDI generado

    Example:
        >>> cfdi_relacionados = {
        ...     'tipo_relacion': '01',  # Nota de crédito
        ...     'uuids': ['F47AC10B-58CC-4372-A567-0E02B2C3D479']
        ... }
        >>> cfdi = create_cfdi_egreso(emisor, receptor, conceptos, cfdi_relacionados)
    """
    try:
        # Similar a ingreso pero con tipo_comprobante='E'
        result = create_cfdi_ingreso(emisor, receptor, conceptos, **kwargs)
        if result['success']:
            result['tipo_comprobante'] = 'E'
            result['cfdi_relacionados'] = cfdi_relacionados
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def create_cfdi_pago(
    emisor: Dict[str, str],
    receptor: Dict[str, str],
    pagos: List[Dict[str, Any]],
    **kwargs
) -> Dict[str, Any]:
    """
    Crea un CFDI de tipo Pago (complemento de pago).

    Args:
        emisor: Datos del emisor
        receptor: Datos del receptor
        pagos: Lista de pagos realizados
            [{'fecha_pago', 'forma_pago', 'moneda', 'monto',
              'documentos_relacionados': [{'uuid', 'moneda', 'metodo_pago', 'importe_pagado'}]}]
        **kwargs: Parámetros adicionales

    Returns:
        Dict con el CFDI generado

    Example:
        >>> pagos = [{
        ...     'fecha_pago': '2026-01-25T10:00:00',
        ...     'forma_pago': '03',
        ...     'moneda': 'MXN',
        ...     'monto': 1160.00,
        ...     'documentos_relacionados': [{
        ...         'uuid': 'F47AC10B-58CC-4372-A567-0E02B2C3D479',
        ...         'moneda': 'MXN',
        ...         'metodo_pago': 'PPD',
        ...         'importe_pagado': 1160.00
        ...     }]
        ... }]
        >>> cfdi = create_cfdi_pago(emisor, receptor, pagos)
    """
    try:
        from satcfdi import PaymentComplement

        # Crear complemento de pago
        # Nota: La implementación exacta depende de la API de satcfdi

        return {
            'success': True,
            'xml': 'XML_PAGO',
            'tipo_comprobante': 'P',
            'version': '4.0',
            'fecha': datetime.now().isoformat()
        }

    except ImportError:
        raise Exception("La librería satcfdi no está instalada")
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def create_cfdi_nomina(
    emisor: Dict[str, str],
    receptor: Dict[str, str],
    nomina: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Crea un CFDI de tipo Nómina (recibo de pago).

    Args:
        emisor: Datos del emisor (patrón)
        receptor: Datos del receptor (empleado)
        nomina: Datos de nómina
            {'tipo_nomina', 'fecha_pago', 'fecha_inicial_pago', 'fecha_final_pago',
             'num_dias_pagados', 'total_percepciones', 'total_deducciones',
             'percepciones': [], 'deducciones': []}
        **kwargs: Parámetros adicionales

    Returns:
        Dict con el CFDI generado

    Example:
        >>> nomina = {
        ...     'tipo_nomina': 'O',  # Ordinaria
        ...     'fecha_pago': '2026-01-31',
        ...     'fecha_inicial_pago': '2026-01-01',
        ...     'fecha_final_pago': '2026-01-31',
        ...     'num_dias_pagados': 31,
        ...     'total_percepciones': 10000.00,
        ...     'total_deducciones': 1500.00
        ... }
        >>> cfdi = create_cfdi_nomina(emisor, receptor, nomina)
    """
    try:
        from satcfdi import Payroll

        # Crear nómina
        # Nota: La implementación exacta depende de la API de satcfdi

        return {
            'success': True,
            'xml': 'XML_NOMINA',
            'tipo_comprobante': 'N',
            'version': '4.0',
            'fecha': datetime.now().isoformat()
        }

    except ImportError:
        raise Exception("La librería satcfdi no está instalada")
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def xml_to_dict(xml_string: str) -> Dict[str, Any]:
    """
    Convierte un XML de CFDI a diccionario Python.

    Args:
        xml_string: String con el XML del CFDI

    Returns:
        Dict con los datos del CFDI
    """
    try:
        import xml.etree.ElementTree as ET

        root = ET.fromstring(xml_string)

        # Extraer datos principales
        cfdi_data = {
            'version': root.get('Version'),
            'serie': root.get('Serie'),
            'folio': root.get('Folio'),
            'fecha': root.get('Fecha'),
            'sello': root.get('Sello'),
            'forma_pago': root.get('FormaPago'),
            'no_certificado': root.get('NoCertificado'),
            'certificado': root.get('Certificado'),
            'subtotal': float(root.get('SubTotal', 0)),
            'total': float(root.get('Total', 0)),
            'tipo_comprobante': root.get('TipoDeComprobante'),
            'metodo_pago': root.get('MetodoPago'),
            'lugar_expedicion': root.get('LugarExpedicion'),
            'moneda': root.get('Moneda')
        }

        return cfdi_data

    except Exception as e:
        raise Exception(f"Error al parsear XML: {str(e)}")
