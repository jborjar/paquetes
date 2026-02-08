"""
Ejemplo de consulta de BusinessPartners (Proveedores) usando sapb1sl.

Este script muestra cómo consultar proveedores con todos los campos
usando el parámetro inlinecount para obtener el total.
"""
from sapb1sl import query_entities

# Lista de campos a seleccionar
campos_proveedor = [
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
]


def obtener_proveedores():
    """
    Obtiene todos los proveedores (CardType='S') con campos completos.

    Equivalente a:
    BusinessPartners?$inlinecount=allpages&$filter=CardType eq 'S'&$select=...
    """

    # Construir string de select
    select_str = ','.join(campos_proveedor)

    # Realizar query con inlinecount
    resultado = query_entities(
        entity_name='BusinessPartners',
        filter="CardType eq 'S'",  # 'S' = Supplier (Proveedor)
        select=select_str,
        inlinecount=True,  # Incluir total count
        max_page_size=0    # Sin límite, traer todos
    )

    # El resultado es un dict con 'value' y 'count'
    proveedores = resultado['value']
    total = resultado['count']

    print(f"Total de proveedores: {total}")
    print(f"Proveedores obtenidos: {len(proveedores)}")
    print()

    # Mostrar primeros 5 proveedores
    print("Primeros 5 proveedores:")
    for i, prov in enumerate(proveedores[:5], 1):
        print(f"{i}. {prov['CardCode']}: {prov['CardName']}")
        print(f"   Ciudad: {prov.get('City', 'N/A')}")
        print(f"   Email: {prov.get('EmailAddress', 'N/A')}")
        print()

    return resultado


def obtener_proveedores_helper():
    """
    Alternativa usando execute_query (helper de alto nivel).
    """
    from sapb1sl import execute_query

    resultado = execute_query(
        entity_name='BusinessPartners',
        conditions={'CardType': 'S'},  # Proveedores
        select_fields=campos_proveedor,
        inlinecount=True,
        max_page_size=0
    )

    print(f"Total con execute_query: {resultado['count']}")
    return resultado


def obtener_proveedores_activos():
    """
    Obtiene solo proveedores activos (Valid='tYES').
    """
    from sapb1sl import execute_query

    resultado = execute_query(
        entity_name='BusinessPartners',
        conditions={
            'CardType': 'S',      # Proveedores
            'Valid': 'tYES'       # Activos
        },
        select_fields=['CardCode', 'CardName', 'EmailAddress', 'City'],
        inlinecount=True
    )

    print(f"Proveedores activos: {resultado['count']}")
    return resultado


if __name__ == '__main__':
    print("=" * 80)
    print("CONSULTA DE PROVEEDORES - SAP B1 Service Layer")
    print("=" * 80)
    print()

    # Opción 1: Usando query_entities directamente
    print("1. Usando query_entities():")
    resultado1 = obtener_proveedores()

    print()
    print("-" * 80)
    print()

    # Opción 2: Usando execute_query (helper)
    print("2. Usando execute_query() helper:")
    resultado2 = obtener_proveedores_helper()

    print()
    print("-" * 80)
    print()

    # Opción 3: Solo proveedores activos
    print("3. Solo proveedores activos:")
    resultado3 = obtener_proveedores_activos()

    print()
    print("=" * 80)
    print("✓ Consultas completadas")
