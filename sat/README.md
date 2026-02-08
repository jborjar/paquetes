# Paquete SAT - Facturación Electrónica CFDI

Módulo completo para trabajar con CFDI (Comprobante Fiscal Digital por Internet) y servicios del SAT de México.

## Características

✓ **Generación de CFDI 4.0** - Ingreso, Egreso, Pago, Nómina
✓ **Validación** - Estructura XML, sellos digitales, consulta con SAT
✓ **Timbrado con PAC** - Finkok, SW Sapien, Diverza
✓ **Descarga masiva** - Automatización de descarga desde portal del SAT
✓ **Validación de RFC** - Formato, listas negras 69-B, contribuyentes no localizados
✓ **CSF** - Obtención y validación de Constancia de Situación Fiscal
✓ **Portable y genérico** - Usa variables de entorno, sin dependencias internas

## Instalación

```bash
# Librería principal para CFDI
pip install satcfdi

# Dependencias adicionales
pip install requests zeep pdfplumber

# Todas las dependencias
pip install satcfdi requests zeep pdfplumber
```

## Configuración

### Variables de Entorno

```env
# Emisor (para generación de CFDI)
SAT_EMISOR_RFC=XAXX010101000
SAT_EMISOR_NOMBRE=MI EMPRESA SA DE CV
SAT_CERTIFICADO_PATH=/ruta/certificado.cer
SAT_KEY_PATH=/ruta/llave.key
SAT_KEY_PASSWORD=password

# PAC (para timbrado)
SAT_PAC_PROVIDER=finkok          # finkok, sw, diverza
SAT_PAC_USERNAME=usuario@empresa.com
SAT_PAC_PASSWORD=password_pac
SAT_PAC_MODE=production          # test o production

# FIEL (para descarga masiva y CSF)
SAT_FIEL_CER=/ruta/fiel.cer
SAT_FIEL_KEY=/ruta/fiel.key
SAT_FIEL_PASSWORD=password_fiel
```

## Uso Básico

### 1. Generar CFDI

```python
from paquetes.sat import create_cfdi_ingreso

emisor = {
    'rfc': 'XAXX010101000',
    'nombre': 'MI EMPRESA SA DE CV',
    'regimen_fiscal': '601'
}

receptor = {
    'rfc': 'XEXX010101000',
    'nombre': 'CLIENTE SA DE CV',
    'uso_cfdi': 'G03',
    'domicilio_fiscal_receptor': '12345',
    'regimen_fiscal_receptor': '612'
}

conceptos = [{
    'clave_prod_serv': '01010101',
    'cantidad': 1,
    'clave_unidad': 'E48',
    'descripcion': 'Servicio de consultoría',
    'valor_unitario': 1000.00,
    'importe': 1000.00,
    'objeto_imp': '02',
    'impuestos': {
        'traslados': [{
            'base': 1000.00,
            'impuesto': '002',
            'tipo_factor': 'Tasa',
            'tasa_o_cuota': 0.16,
            'importe': 160.00
        }]
    }
}]

# Generar CFDI
result = create_cfdi_ingreso(
    emisor=emisor,
    receptor=receptor,
    conceptos=conceptos,
    lugar_expedicion='12345'
)

if result['success']:
    xml_cfdi = result['xml']
    print(f"CFDI generado. Total: ${result['total']}")
```

### 2. Timbrar CFDI

```python
from paquetes.sat import stamp_cfdi

result = stamp_cfdi(
    xml_string=xml_cfdi,
    pac_provider='finkok',
    username='usuario@empresa.com',
    password='password_pac'
)

if result['success']:
    uuid = result['timbre']['uuid']
    xml_timbrado = result['xml']
    print(f"CFDI timbrado. UUID: {uuid}")
```

### 3. Validar CFDI

```python
from paquetes.sat import validate_cfdi_structure, validate_cfdi_with_sat

# Validar estructura
result = validate_cfdi_structure(xml_timbrado)
if result['valid']:
    print("Estructura válida")
else:
    print(f"Errores: {result['errors']}")

# Validar contra el SAT
result = validate_cfdi_with_sat(
    uuid=uuid,
    rfc_emisor='XAXX010101000',
    rfc_receptor='XEXX010101000',
    total=1160.00
)
print(f"Estado en SAT: {result['estado_cfdi']}")
```

### 4. Descargar CFDIs del SAT

```python
from paquetes.sat import download_cfdi_full_process

result = download_cfdi_full_process(
    rfc='XAXX010101000',
    fecha_inicio='2026-01-01',
    fecha_fin='2026-01-31',
    tipo='emitidos',
    output_dir='./mis_facturas',
    certificado='fiel.cer',
    key_file='fiel.key',
    key_password='password'
)

if result['success']:
    print(f"Descargados {result['total_cfdis']} CFDIs")
```

### 5. Validar RFC

```python
from paquetes.sat import validate_rfc_format, is_rfc_safe_to_transact

# Validar formato
result = validate_rfc_format('XAXX010101000')
if result['valid']:
    print(f"RFC válido: {result['tipo']}")

# Verificar si es seguro transaccionar
result = is_rfc_safe_to_transact('XAXX010101000')
if result['seguro']:
    print("RFC aprobado para transacciones")
else:
    print(f"Riesgos detectados: {result['riesgos']}")
```

### 6. Obtener CSF

```python
from paquetes.sat import get_csf
import base64

csf = get_csf(
    rfc='XAXX010101000',
    certificado='fiel.cer',
    key_file='fiel.key',
    key_password='password'
)

if csf['success']:
    # Guardar PDF
    with open('csf.pdf', 'wb') as f:
        f.write(base64.b64decode(csf['pdf']))

    # Ver datos fiscales
    print(f"Nombre: {csf['datos_fiscales']['nombre_razon_social']}")
    print(f"Regímenes: {csf['datos_fiscales']['regimenes']}")
```

## Validador de CSF (Constancia de Situación Fiscal)

El módulo `csf_validator.py` proporciona validación avanzada de archivos PDF de Constancias de Situación Fiscal del SAT.

### Funcionalidades del Validador

- Extracción de datos de PDFs de CSF
- Validación de formato de RFC
- Consulta de situación fiscal en el SAT
- Verificación en listas negras (69-B)
- Generación de reportes HTML profesionales
- Completamente portable y genérico

### Dependencias Adicionales

```bash
pip install pdfplumber
```

### Uso del Validador

#### Validación Completa con Reporte HTML

```python
from paquetes.sat.csf_validator import validate_csf_full

# Validación completa con reporte HTML automático
result = validate_csf_full(
    pdf_file='constancia.pdf',
    expected_rfc='XAXX010101000'
)

if result['success']:
    data = result['validation_data']
    print(f"RFC: {data['rfc']}")
    print(f"Estado: {data['estado']}")
    print(f"Seguro transaccionar: {data['seguro_transaccionar']}")
    print(f"Reporte HTML: {result['html_file']}")
```

#### Validación con Nombre de Reporte Personalizado

```python
from paquetes.sat.csf_validator import validate_csf_full

result = validate_csf_full(
    pdf_file='constancia.pdf',
    expected_rfc='XAXX010101000',
    output_html='mi_reporte_csf.html'
)
```

#### Solo Validación (Sin Reporte HTML)

```python
from paquetes.sat.csf_validator import validate_csf_from_pdf

data = validate_csf_from_pdf('constancia.pdf', 'XAXX010101000')

if data['success']:
    print(f"RFC válido: {data['formato_valido']}")
    print(f"Seguro: {data['seguro_transaccionar']}")
    print(f"Riesgos: {data['riesgos']}")
```

#### Solo Generar Reporte HTML

```python
from paquetes.sat.csf_validator import validate_csf_from_pdf, generate_html_report

# 1. Validar
data = validate_csf_from_pdf('constancia.pdf')

# 2. Generar HTML
result = generate_html_report(data, 'reporte.html')
print(f"Reporte: {result['html_file']}")
```

### Estructura de Datos del Validador

#### validate_csf_from_pdf()

```python
{
    'success': bool,                    # True si la validación fue exitosa
    'rfc': str,                         # RFC validado
    'csf_rfc': str,                     # RFC extraído del PDF
    'csf_nombre': str,                  # Nombre extraído del PDF
    'formato_valido': bool,             # RFC tiene formato válido
    'tipo_persona': str,                # 'Persona Física' o 'Persona Moral'
    'longitud': int,                    # 12 o 13 caracteres
    'estado': str,                      # 'Activo', 'Inactivo', etc.
    'activo': bool,                     # Contribuyente activo
    'nombre': str,                      # Nombre/Razón Social del SAT
    'regimenes': list,                  # Lista de regímenes fiscales
    'seguro_transaccionar': bool,       # Es seguro hacer negocios
    'riesgos': list,                    # Lista de riesgos detectados
    'csf_valida': bool,                 # CSF es válida
    'csf_errores': list,                # Errores en la CSF
    'csf_warnings': list,               # Advertencias de la CSF
    'fecha_validacion': str             # Fecha/hora de validación
}
```

#### validate_csf_full()

```python
{
    'success': bool,
    'validation_data': dict,            # Datos de validate_csf_from_pdf()
    'html_file': str,                   # Ruta del reporte HTML generado
    'html_size_bytes': int,             # Tamaño del archivo HTML
    'error': str                        # Mensaje de error (si falló)
}
```

### Reporte HTML

El reporte HTML incluye:

- Diseño moderno con gradientes
- Información organizada en cards
- Badges de estado con colores
- Responsive (móvil y desktop)
- Optimizado para impresión

#### Secciones del Reporte:

1. **Validación de RFC** - Formato, tipo, longitud
2. **Situación Fiscal** - Estado, nombre, regímenes
3. **Validación para Transacciones** - Seguro/riesgos
4. **Datos de la CSF** - Información extraída del PDF
5. **Validación de CSF** - Errores y advertencias
6. **Resumen Final** - Conclusión y recomendaciones

### Casos de Uso del Validador

#### Validar Proveedor

```python
from paquetes.sat.csf_validator import validate_csf_full

# Cliente envía su CSF
result = validate_csf_full('csf_proveedor.pdf')

if result['success']:
    data = result['validation_data']

    if not data['seguro_transaccionar']:
        print("PROVEEDOR CON RIESGOS:")
        for riesgo in data['riesgos']:
            print(f"  - {riesgo}")
        print("Solicitar CSF actualizada")
    else:
        print("Proveedor validado - Proceder con negocio")
```

#### Auditoría Masiva

```python
from paquetes.sat.csf_validator import validate_csf_full
from pathlib import Path

# Validar todos los PDFs en una carpeta
pdf_folder = Path('csf_proveedores')

for pdf in pdf_folder.glob('*.pdf'):
    print(f"\nValidando: {pdf.name}")

    result = validate_csf_full(str(pdf))

    if result['success']:
        data = result['validation_data']
        status = "OK" if data['seguro_transaccionar'] else "RIESGOS"
        print(f"  {data['rfc']}: {status}")

        if data['riesgos']:
            for riesgo in data['riesgos']:
                print(f"    - {riesgo}")
```

#### API Endpoint

```python
from fastapi import FastAPI, UploadFile
from paquetes.sat.csf_validator import validate_csf_full
import tempfile
import os

app = FastAPI()

@app.post("/api/validar-csf")
async def validar_csf(file: UploadFile):
    # Guardar PDF temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # Validar
    result = validate_csf_full(tmp_path)

    # Limpiar
    os.unlink(tmp_path)

    return {
        'rfc': result['validation_data']['rfc'],
        'estado': result['validation_data']['estado'],
        'seguro': result['validation_data']['seguro_transaccionar'],
        'riesgos': result['validation_data']['riesgos']
    }
```

### Integración del Validador con Otros Módulos

#### Con MSSQL

```python
from paquetes.sat.csf_validator import validate_csf_from_pdf
from paquetes.mssql import execute_query

# Validar y guardar en base de datos
data = validate_csf_from_pdf('proveedor.pdf')

if data['success']:
    query = """
        INSERT INTO proveedores_validados
        (rfc, nombre, estado, seguro, fecha_validacion)
        VALUES (?, ?, ?, ?, ?)
    """
    params = (
        data['rfc'],
        data['nombre'],
        data['estado'],
        data['seguro_transaccionar'],
        data['fecha_validacion']
    )
    execute_query(query, params)
```

#### Con SAP Business One

```python
from paquetes.sat.csf_validator import validate_csf_from_pdf
from paquetes.sapb1sl import get_business_partner

# Validar proveedor antes de crear en SAP
data = validate_csf_from_pdf('nuevo_proveedor.pdf')

if data['seguro_transaccionar']:
    # Crear proveedor en SAP
    bp = get_business_partner(data['rfc'])
    print(f"Proveedor validado: {bp['CardName']}")
else:
    print("No crear proveedor - RFC con riesgos")
```

### Notas Importantes del Validador

1. **Requiere conexión al SAT**: El módulo consulta el SAT en tiempo real para obtener información actualizada

2. **PDF debe tener texto extraíble**: No funciona con imágenes escaneadas sin OCR

3. **Riesgos detectados**:
   - **Lista 69-B**: RFC con operaciones inexistentes (PELIGRO)
   - **No localizado**: RFC no encontrado por el SAT
   - **Sin certificados**: No puede emitir CFDIs

4. **CSF vigente**: Se recomienda CSF con menos de 90 días de emisión

### Pruebas del Validador

```bash
# Desde el contenedor
docker exec -w /app api-mcp python3 -m paquetes.tests.sat.test_csf_validator archivo.pdf

# Desde el host
cd software/app
python3 -m paquetes.tests.sat.test_csf_validator archivo.pdf XAXX010101000
```

## API Completa

### Generación de CFDI (5 funciones)

| Función | Descripción |
|---------|-------------|
| `create_cfdi_ingreso()` | Genera CFDI de ingreso (factura) |
| `create_cfdi_egreso()` | Genera CFDI de egreso (nota de crédito) |
| `create_cfdi_pago()` | Genera complemento de pago |
| `create_cfdi_nomina()` | Genera recibo de nómina |
| `xml_to_dict()` | Convierte XML CFDI a diccionario |

### Validación (5 funciones)

| Función | Descripción |
|---------|-------------|
| `validate_cfdi_structure()` | Valida estructura XML según SAT |
| `validate_digital_seal()` | Verifica sello digital |
| `validate_cfdi_with_sat()` | Consulta estado en el SAT |
| `extract_cfdi_data()` | Extrae datos del XML |
| `validate_rfc_format_validator()` | Valida formato de RFC |

### Timbrado con PAC (3 funciones)

| Función | Descripción |
|---------|-------------|
| `stamp_cfdi()` | Timbra CFDI con PAC |
| `cancel_cfdi()` | Cancela CFDI timbrado |
| `get_stamp_status()` | Consulta estado de timbrado |

### Descarga Masiva (5 funciones)

| Función | Descripción |
|---------|-------------|
| `request_download()` | Solicita descarga al SAT |
| `check_download_status()` | Verifica estado de solicitud |
| `download_packages()` | Descarga paquetes ZIP |
| `extract_packages()` | Extrae CFDIs de los ZIP |
| `download_cfdi_full_process()` | Proceso completo automatizado |

### RFC y Listas (6 funciones)

| Función | Descripción |
|---------|-------------|
| `validate_rfc_format()` | Valida formato de RFC |
| `check_rfc_in_blacklist_69b()` | Verifica lista negra 69-B |
| `check_rfc_status_in_sat()` | Consulta estado en SAT |
| `check_multiple_rfcs()` | Valida múltiples RFCs |
| `download_blacklist_69b()` | Descarga lista 69-B |
| `is_rfc_safe_to_transact()` | Recomendación de transacción |

### Constancia Situación Fiscal (4 funciones)

| Función | Descripción |
|---------|-------------|
| `get_csf()` | Obtiene CSF del SAT |
| `parse_csf_pdf()` | Extrae datos de PDF de CSF |
| `validate_csf()` | Valida CSF |
| `get_fiscal_situation_summary()` | Resumen situación fiscal |

## Ejemplos Avanzados

### Flujo Completo de Facturación

```python
from paquetes.sat import (
    create_cfdi_ingreso,
    stamp_cfdi,
    validate_cfdi_with_sat,
    is_rfc_safe_to_transact
)

# 1. Validar cliente
cliente_valido = is_rfc_safe_to_transact('XEXX010101000')
if not cliente_valido['seguro']:
    print(f"Cliente con riesgos: {cliente_valido['riesgos']}")
    exit(1)

# 2. Generar CFDI
cfdi = create_cfdi_ingreso(emisor, receptor, conceptos, lugar_expedicion='12345')
if not cfdi['success']:
    print(f"Error: {cfdi['error']}")
    exit(1)

# 3. Timbrar
timbre = stamp_cfdi(cfdi['xml'])
if not timbre['success']:
    print(f"Error al timbrar: {timbre['error']}")
    exit(1)

# 4. Validar en SAT
validacion = validate_cfdi_with_sat(
    uuid=timbre['timbre']['uuid'],
    rfc_emisor=emisor['rfc'],
    rfc_receptor=receptor['rfc'],
    total=cfdi['total']
)

if validacion['estado_cfdi'] == 'Vigente':
    print(f"✓ Factura exitosa. UUID: {timbre['timbre']['uuid']}")
```

### Descarga y Procesamiento Masivo

```python
from paquetes.sat import download_cfdi_full_process, extract_cfdi_data

# Descargar CFDIs del mes
result = download_cfdi_full_process(
    rfc='XAXX010101000',
    fecha_inicio='2026-01-01',
    fecha_fin='2026-01-31',
    tipo='emitidos',
    output_dir='./facturas_enero'
)

# Procesar cada CFDI
if result['success']:
    for archivo in result['archivos']:
        if archivo.endswith('.xml'):
            with open(archivo, 'r') as f:
                xml = f.read()
                datos = extract_cfdi_data(xml)
                print(f"Factura: {datos['serie']}-{datos['folio']}, Total: ${datos['total']}")
```

## Portabilidad

Este paquete es completamente portable:

✓ Sin dependencias de config.py
✓ Configurable por variables de entorno
✓ Puede copiarse a cualquier proyecto Python
✓ No requiere estructura específica del proyecto

## Troubleshooting

### Error: "La librería satcfdi no está instalada"

```bash
pip install satcfdi
```

### Error: "Credenciales del PAC no configuradas"

Configurar variables de entorno o pasar credenciales directamente:

```python
stamp_cfdi(
    xml,
    pac_provider='finkok',
    username='usuario@empresa.com',
    password='password'
)
```

### Error al descargar del SAT

Verificar que:
- La FIEL esté vigente
- Las fechas estén en formato YYYY-MM-DD
- El rango no exceda 31 días

## Documentación Adicional

- [Especificaciones CFDI 4.0 del SAT](http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/Anexo_20_Guia_de_llenado_CFDI.pdf)
- [Catálogos CFDI](http://www.sat.gob.mx/sitio_internet/cfd/catalogos/catCFDI.xsd)
- [API satcfdi](https://github.com/SAT-CFDI/python-satcfdi)

---

**Versión:** 1.0.0
**Última actualización:** 2026-01-31
