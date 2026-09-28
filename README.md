# CyberWarn

**CyberWarn** - Инструмент для автоматизированного выявления угроз кибер-безопасности, основанный на сканировании веб-приложений и проведении социотехнического тестирования (Social Engineering).  

Инструмент разработан с упором на легковесную модульную архитектуру, отсутствие тяжелых зависимостей и удобную автоматизацию рутинных задач этичного хакинга.  

## Disclaimer
> Данный инструмент разработан исключительно для проведения санкционированного аудита безопасности и легального тестирования на проникновение. Автор проекта не несет ответственности за любой возможный ущерб, недополученную прибыль или вред, причиненный в результате нецелевого или неправомерного использования инструмента **CyberWarn**. 

## Клонирование/Установка
clone
```sh
git clone https://gitea.com/cyberwarn/cyberwarn && cd cyberwarn
```
установка пакетов
```sh
python3 -m venv venv && source venv/bin/activate && pip install -r packages.txt
```
Тестовый запуск
```sh
python3 -m cyberwarn
```

## Возможности
- Проверка поддоменов  
- Перебор директорий и файлов
- Сканирование плагинов WordPress
- Проверка версии WordPress
- Сбор ссылок с ресурса
- Сбор комментариев HTML с ресурса  
- Brute Force доступов пользователей к веб-приложению
- Фаззиниг заголовков
- Поиск пользователей по нику в социальных сетях(в процессе разработки)
- Клонирование страницы по URL

> Есть возможность добавить прокси в *data/settings.json*

## Тестирование/отладка
Для проверки всех модулей используется tests/check_all_modules
```sh
python3 -m tests.check_all_modules
```
Так же можно добавить произвольный URL для тестирования:
```sh
python3 -m tests.check_all_modules https://example.com
```

## Использование модулей
Для просмотра доступных модулей использовать cyberwarn без аргументов
```sh
python3 -m cyberwarn
```
Вывод будет примерно таким:
```sh
|--------------------------------------------------------
| author:       Rickert155	https://github.com/rickert155
| project:      CyberWarn	GPLv3      
| version:      0.3.2     
|--------------------------------------------------------
| CyberWarn
| [1] Сканер поддоменов: fuzz-subdomains
| [2] Сканер директорий: fuzz-dirs
| [3] Сборщик ссылок: get-links
| [4] Сборщик комментариев: get-comments
| [5] Сканер плагинов WordPress: wp-plugins
| [6] Сканер версии WordPress: wp-version
| [7] Проверка уязвимых версий плагинов CMS: vuln-checker
| [8] Brute Force логина/пароля: bruteforce-login
| [9] Фаззинг заголовков: bad-headers
| [10] Поиск по никнейму: search-user
| [11] Клонирование страницы: clone-page
```
Для просмотри с примерами команд:
```sh
python3 -m cyberwarn --help
```


### Анализ CMS
**Сканер плагинов WordPress**  
Пример использования:
```sh
python3 -m cyberwarn wp-plugins --url=https://127.0.0.1:3000 --workers=20
```
**Сканер версии WordPress**  
Пример использования:
```sh
python3 -m cyberwarn wp-version --url=http://127.0.0.1:3000
```

**Проверка на наличие уязвимых плагинов**  
Аргументом *--plugins-json* необходимо передать json файл, содержащий список, описывающий плагины приложения. Необходимые поля:  
- plugin
- version  
Опциональные поля:  
- url_plugin  
url с тестируемого сайта, пример для WordPress: https://example.com/wp-content/plugins/plugin_name  

Подобный файл генерирует модуль *wp-plugins*  

Аргументом *--cms* необходимо указать CMS.  
Пример использования:
```sh
python3 -m cyberwarn vuln-checker --plugins-json=app.plugins.json --cms=wordpress
```

### Анализ возможных поверхностей атак
**Сканер поддоменов**  
Пример использования:
```sh
python3 -m cyberwarn fuzz-subdomains --url=https://example.com --wordlist=data/wordlist/web/subdomains.txt --workers=20
```

**Сканер директорий**  
```sh
python3 -m cyberwarn fuzz-dirs --url=https://example.com --wordlist=data/wordlist/web/dir.txt --workers=20
```

**Фаззинг заголовков**  
Модуль предназначен для проверки ответов приложения на различную полезную нагрузку в заголовках HTTP запросов.  
Необходимо два файл:  
- **Исходный файл** - передается значением для параметра --headers
- **Файл с полезной нагрузкой** - передается значением для параметра --payloads  

Модуль считывает построчно для каждого запроса строку с заголовком - в каждом запросе используется исходный запрос + новый заголовок. Если в исходном файле уже есть заголовок из payloads - в таком случае заголовок будет заменен тем, что используется в payloads.  

Для тестирования подготовлены два файл с заголовками:  
- data/bad_headers_temapltes/source-headers.txt
- data/bad_headers_temapltes/user-payloads.txt  

Заголовки запролняются через двоеточие(ключ: значение)
```txt
Host: www.example.com
User-Agent: Test user-agent
```
Если заголовок **User-Agent** отсутствует - он будет сгенерирован автоматически.  

Пример использования: 
```sh
python3 -m cyberwarn bad-headers --url=https://example.com --headers=data/bad_headers_temapltes/source-headers.txt --payloads=data/bad_headers_temapltes/user-payloads.txt
```

**Сбор ссылок с ресурса**  
Пример использования:
```sh
python3 -m cyberwarn get-links --url=http://example.com
```
**Сбор комментариев с ресурса**  
Пример использования:
```sh
python3 -m cyberwarn get-comments --url=https://example.com
```

### Взлом приложения, подбор учетных данных
**Подбор логина/пароля формы авторизации**  
Пример использования:
```sh
python3 -m cyberwarn bruteforce-login --url=https://example.com/login --users=data/wordlist/users.txt --passwords=data/wordlist/auth/passwords.txt --form="username=[USER]&password=[PASSWORD]" --fm="Invalid username or password."
```

### Фишинг/Социальная инженерия
**Клонирование страницы**  
Пример использования:
```sh
python3 -m cyberwarn clone-page --url=https://example.com --page-name=index.html
```
Аргумент *--page-name* - имя, под которым будет сохранена страница. Модуль выведет относительный путь сохранения страницы:
```sh
Результат: sites/example.com/example.html
```

## Запуск в контейнере
Для запуска в контенере подготовлен Containerfile.  
Собираем образ:
```sh
podman build -t cyberwarn -f Containerfile
```
Запускаем контейнер на основе нашего образа, монтируя директорию data:
```sh
podman run --rm -it -v $PWD/data:/root/cyberwarn/data cyberwarn
```
> Образ собирается вместе с vim и fish для комфортной работы в контейнере

## Готовый образ Podman/Docker
Наиболее протестированные версии доступны в формате образов. Доступны на github и docker.io
```sh
podman pull ghcr.io/rickert155/cyberwarn:0.3.0
```
Так же вы можете брать образ из Docker Hub
```sh
podman pull docker.io/cyberwarn/cyberwarn:0.3.0
```
