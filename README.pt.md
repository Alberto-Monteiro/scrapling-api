# 🕷️ Scrapling API Microservice (Docker & FastAPI)

🌐 **[English](README.md) | [Português](README.pt.md)**

Este repositório contém um **Microsserviço de Web Scraping de alta performance** pronto para produção, construído sobre o framework **FastAPI** e a biblioteca **Scrapling**. 

Ele foi desenhado especificamente para ser consumido por outras linguagens de programação (como **Java**, C#, Node.js, etc.) rodando de forma isolada dentro do Docker com todos os navegadores e camuflagens anti-bot pré-configurados.

---

## 🚀 Como Iniciar o Serviço

Para compilar e subir o serviço em segundo plano (modo daemon) na sua máquina ou servidor:

```bash
docker compose up --build -d
```

O serviço estará disponível imediatamente na porta **`8000`** (`http://localhost:8000`).

---

## 🌐 Endpoints Disponíveis

A API expõe dois endpoints principais via `POST`:

### 1. `POST /fetch` (Obter HTML Renderizado)
Baixa e renderiza a página completa, retornando o HTML puro. Ideal se você já usa uma biblioteca de parsing no seu cliente (como o **Jsoup** no Java).

* **Payload Exemplo:**
```json
{
    "url": "https://quotes.toscrape.com/js/",
    "fetcher": "stealthy"
}
```

* **Resposta:**
```json
{
    "url": "https://quotes.toscrape.com/js/",
    "fetcher_used": "stealthy",
    "status_code": 200,
    "html": "<html>...</html>"
}
```

---

### 2. `POST /extract` (Obter Dados Estruturados em JSON)
Faz a busca e extrai cirurgicamente os dados do HTML direto no microsserviço, devolvendo um JSON limpo contendo apenas os dados solicitados.

* **Payload Exemplo:**
```json
{
    "url": "https://quotes.toscrape.com/",
    "fetcher": "static",
    "selectors": {
        "titulo": "h1 a::text",
        "primeira_frase": ".quote .text::text"
    }
}
```

* **Resposta:**
```json
{
    "url": "https://quotes.toscrape.com/",
    "fetcher_used": "static",
    "status_code": 200,
    "data": {
        "titulo": "Quotes to Scrape",
        "primeira_frase": "“The world as we have created it is a process of our thinking...”"
    }
}
```

---

## 🛠️ Parâmetros do Payload

Ambos os endpoints aceitam as seguintes configurações opcionais:

| Campo | Tipo | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| **`url`** | *String* | *(Obrigatório)* | A URL do site que você deseja raspar. |
| **`fetcher`** | *String* | `"stealthy"` | Motor de busca: `"static"` (HTTP rápido), `"dynamic"` (Navegador JS), ou `"stealthy"` (Navegador ninja anti-bot). |
| **`timeout`** | *Integer* | `30000` | Tempo máximo de espera em milissegundos. |
| **`proxy`** | *String* | `null` | URL do seu proxy (Ex: `http://usuario:senha@p.webshare.io:80`). |
| **`cookies`** | *String/Object*| `null` | String de cookies copiada do seu navegador para manter sessões ou logar. |
| **`selectors`** | *Object* | *(Apenas /extract)* | Dicionário contendo os apelidos e os seletores CSS/XPath. |

---

## 🎯 Sintaxes Avançadas de Seletores (Scrapling)

Para extrair dados específicos das tags HTML de forma precisa no parâmetro `"selectors"`:

* **Obter o texto de dentro de uma tag:** Use `::text` no final.
  * *Exemplo:* `"titulo": "h1::text"` ➔ Retorna `"Título Exemplo"`
* **Obter a URL de um link (`href`):** Use `::attr(href)` no final.
  * *Exemplo:* `"link_produto": ".product_pod h3 a::attr(href)"` ➔ Retorna `"catalogue/..."`
* **Obter o link de uma imagem (`src`):** Use `::attr(src)` no final.
  * *Exemplo:* `"url_foto": "img.thumbnail::attr(src)"`
* **Obter o valor de um campo de metadado (SEO):**
  * *Exemplo:* `"preco": "meta[property=\"product:price:amount\"]::attr(content)"`

---

## 🥷 Exemplos Práticos Avançados

### A. Raspagem Dinâmica e JS-heavy (Sandbox de Citações com JS)
Para raspar elementos que dependem 100% de execução de JavaScript na página usando o `"fetcher": "dynamic"` ou `"stealthy"`:

```bash
curl --location 'http://localhost:8000/extract' \
--header 'Content-Type: application/json' \
--data '{
    "url": "https://quotes.toscrape.com/js/",
    "fetcher": "dynamic",
    "selectors": {
        "citacoes": ".quote .text::text",
        "autores": ".quote .author::text"
    }
}'
```

### B. Raspagem de Listas, Links e Imagens (Livraria Sandbox)
Exemplo extraindo títulos, preços, URLs de detalhe e links de imagem de uma lista de produtos de forma estática:

```bash
curl --location 'http://localhost:8000/extract' \
--header 'Content-Type: application/json' \
--data '{
    "url": "https://books.toscrape.com/",
    "fetcher": "static",
    "selectors": {
        "titulos_livros": ".product_pod h3 a::text",
        "links_detalhe": ".product_pod h3 a::attr(href)",
        "imagens_capa": ".product_pod .image_container img::attr(src)",
        "precos": ".product_pod .price_color::text"
    }
}'
```

### C. Raspagem Avançada com Proxy & Cookies Combinados
Quando você precisa raspar um site complexo que exige login/sessão ativa e, ao mesmo tempo, proteção de reputação de IP (para não ser bloqueado):

```bash
curl --location 'http://localhost:8000/extract' \
--header 'Content-Type: application/json' \
--data '{
    "url": "https://httpbin.org/anything",
    "fetcher": "stealthy",
    "proxy": "http://seu_usuario:sua_senha@p.webshare.io:80",
    "cookies": "session_id=12345abcde; user_token=98765qwerty; authenticated=true",
    "selectors": {
        "ip_de_saida": "json::attr(origin)",
        "cookies_recebidos": "json::attr(headers.Cookie)"
    }
}'
```
> [!NOTE]
> No exemplo acima, usamos o endpoint `httpbin.org/anything` que atua como um espelho de requisição, retornando exatamente o IP do proxy que foi utilizado no download e os cookies que o microsserviço injetou com sucesso no cabeçalho/navegador.

---

## ☕ Integração com Java (Java 11+)

Exemplo de classe utilitária em Java para disparar a requisição e obter o HTML:

```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class ScraplingClient {
    public static String fetchPageHtml(String targetUrl) throws Exception {
        HttpClient client = HttpClient.newHttpClient();
        
        String jsonPayload = String.format("""
            {
                "url": "%s",
                "fetcher": "stealthy"
            }
            """, targetUrl);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("http://localhost:8000/fetch"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body(); // Retorna o JSON com o HTML renderizado
    }
}
```
