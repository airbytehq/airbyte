# DMP - Eduzz
Conector API Eduzz

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Accounts: Geral |  | No pagination | ✅ |  ❌  |
| MyEduzz: Vendas | id | DefaultPaginator | ✅ |  ✅  |
| MyEduzz: Assinaturas | id | DefaultPaginator | ✅ |  ✅  |
| MyEduzz: Produtos | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-09-27 | | Initial release by [@caio7siqueira](https://github.com/caio7siqueira) via Connector Builder |

</details>
