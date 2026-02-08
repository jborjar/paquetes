"""
Ejemplo de consulta exacta al endpoint BusinessPartners usando sapb1sl.

Este script replica la siguiente consulta OData:
BusinessPartners?$inlinecount=allpages&$filter=CardType eq 'S'&$select=...
"""
from paquetes.sapb1sl import query_entities

# Lista completa de campos según especificación del usuario
CAMPOS_BUSINESSPARTNERS = ','.join([
    'CardCode', 'CardName', 'GroupCode', 'Address', 'ZipCode',
    'MailAddress', 'MailZipCode', 'Phone1', 'Phone2', 'Fax',
    'ContactPerson', 'PayTermsGrpCode', 'CreditLimit', 'MaxCommitment',
    'DiscountPercent', 'FederalTaxID', 'DeductibleAtSource',
    'DeductionPercent', 'DeductionValidUntil', 'PriceListNum',
    'Currency', 'Cellular', 'City', 'County', 'Country',
    'EmailAddress', 'DefaultAccount', 'DefaultBankCode',
    'CurrentAccountBalance', 'OpenDeliveryNotesBalance',
    'OpenOrdersBalance', 'OpenChecksBalance', 'IBAN',
    'CreditCardCode', 'CreditCardNum', 'CreditCardExpiration',
    'DebitorAccount', 'OpenOpportunities', 'Valid', 'Frozen',
    'Block', 'BillToState', 'ShipToState', 'PeymentMethodCode',
    'BackOrder', 'PartialDelivery', 'BlockDunning', 'BankCountry',
    'HouseBank', 'HouseBankCountry', 'HouseBankAccount',
    'ShipToDefault', 'HouseBankBranch', 'VatGroupLatinAmerica',
    'HouseBankIBAN', 'UpdateDate', 'UpdateTime', 'CreateDate',
    'CreateTime'
])


def consultar_proveedores():
    """
    Consulta el endpoint BusinessPartners exactamente como se especificó:

    BusinessPartners?$inlinecount=allpages&$filter=CardType eq 'S'&$select=...

    Donde:
    - $inlinecount=allpages  →  inlinecount=True
    - $filter=CardType eq 'S'  →  filter="CardType eq 'S'"
    - $select=...  →  select=CAMPOS_BUSINESSPARTNERS
    """

    print("Ejecutando consulta a BusinessPartners...")
    print()

    resultado = query_entities(
        entity_name='BusinessPartners',
        filter="CardType eq 'S'",        # Solo proveedores (Suppliers)
        select=CAMPOS_BUSINESSPARTNERS,   # Todos los campos especificados
        inlinecount=True,                 # $inlinecount=allpages
        max_page_size=0                   # Sin límite, traer todos
    )

    # El resultado es un dict con 'value' y 'count'
    proveedores = resultado['value']
    total = resultado['count']

    print(f"✓ Consulta completada exitosamente")
    print()
    print(f"Total de proveedores en SAP B1: {total}")
    print(f"Proveedores obtenidos: {len(proveedores)}")
    print()

    # Mostrar algunos proveedores de ejemplo
    if proveedores:
        print("Primeros 3 proveedores:")
        for i, prov in enumerate(proveedores[:3], 1):
            print(f"\n{i}. {prov['CardCode']} - {prov['CardName']}")
            print(f"   Ciudad: {prov.get('City', 'N/A')}")
            print(f"   País: {prov.get('Country', 'N/A')}")
            print(f"   Email: {prov.get('EmailAddress', 'N/A')}")
            print(f"   Teléfono: {prov.get('Phone1', 'N/A')}")
            print(f"   Activo: {prov.get('Valid', 'N/A')}")
            print(f"   Límite crédito: {prov.get('CreditLimit', 0)}")

    return resultado


def consultar_proveedores_activos():
    """
    Variante: Solo proveedores activos.
    """
    print("\nConsultando solo proveedores ACTIVOS...")
    print()

    resultado = query_entities(
        entity_name='BusinessPartners',
        filter="CardType eq 'S' and Valid eq 'tYES'",  # Activos
        select=CAMPOS_BUSINESSPARTNERS,
        inlinecount=True,
        max_page_size=0
    )

    print(f"✓ Proveedores activos: {resultado['count']}")
    return resultado


def consultar_proveedores_paginado():
    """
    Variante: Con paginación (primeras 100).
    """
    print("\nConsultando proveedores con paginación (top 100)...")
    print()

    resultado = query_entities(
        entity_name='BusinessPartners',
        filter="CardType eq 'S'",
        select='CardCode,CardName,City,EmailAddress',  # Campos reducidos
        inlinecount=True,
        top=100  # Solo primeros 100
    )

    print(f"✓ Total proveedores: {resultado['count']}")
    print(f"✓ Obtenidos en esta página: {len(resultado['value'])}")
    return resultado


if __name__ == '__main__':
    print("=" * 80)
    print("CONSULTA DE BUSINESSPARTNERS - SAP B1 SERVICE LAYER")
    print("=" * 80)
    print()
    print("Endpoint equivalente:")
    print("BusinessPartners?$inlinecount=allpages&$filter=CardType eq 'S'&$select=...")
    print()
    print("-" * 80)
    print()

    try:
        # Consulta principal
        resultado = consultar_proveedores()

        # Variantes
        print("\n" + "=" * 80)
        resultado_activos = consultar_proveedores_activos()

        print("\n" + "=" * 80)
        resultado_paginado = consultar_proveedores_paginado()

        print("\n" + "=" * 80)
        print("✓ Todas las consultas completadas exitosamente")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
