# SP
SPPack repository for DynamicPack mod!

[![img.png](img.png)](https://modrinth.com/mod/dynamicpack)

[![Modrinth Downloads](https://img.shields.io/modrinth/dt/dynamicpack%20?style=flat-square&label=DynamicPack%20on%20Modrinth)](https://modrinth.com/mod/dynamicpack)

# ВНИМАНИЕ
**ТЕКСТ НИЖЕ В ОСНОВНОМ ДЛЯ ТЕХ, КТО БУДЕТ НА ПОСТУ РЕСУРСПАКЕРА СП, А НЕ ДЛЯ ОБЫЧНЫХ ПОЛЬЗОВАТЕЛЕЙ**


## Общий ресурспак СП
Всем привет, это репозиторий-проект Общего Ресурспака СП. Его оригинальный автор Енотис, прородитель - Вецкер

Основа структуры ресурспака это мод DynamicPack, именно для него файлы лежат именно так, но и впринципе
это очень удобно.



## Включённые паки
Не вижу смысла перечислять их в README

Директория `merged_packs` содержит паки. Учтите что DynamicPack собирает все эти паки в один и они не должны конфликтовать!

Внутри директории каждого ресурспака есть файл .rpname_info.txt с метадатой о это паке. DynamicPack скипает их (с.м. #Скрипты)



## Скрипты
### splashes.py
Запускаешь и он "собирает" файл сплешей `splashes-with-metadata.txt` в файл майнкрафта (убирает комментарии) в файл `sp_splashes/assets/minecraft/texts/splashes.txt`


### sppack_auto.py
Разные инструменты, недоделан но он умеет чинить картинки для рабочего anti-aliasing; [*discord post*](https://discord.com/channels/1269289408859734128/1273228126935191654)

А ещё умеет убирать json pretty-print для экономии места

### dynamicpack_auto.py
Файл для апдейта метаданных для мода DynamicPack
(файл общий, MIT License, взят с других репозиториев.)

### files.py
Когда-нибудь я займусь этим... (файлы files.csv и files.csv.gz, а также contents.csv, content_directories.txt и [dynamicpack.repo.build](dynamicpack.repo.build) с [dynamicpack.repo.json](dynamicpack.repo.json) тоже к этому)



## Важные аксиомы
- Использовать пробелы в названиях файлов и папок нельзя!
- Использовать папки имена которых имеют большие буквы нельзя (только в винде это работает кое-как, не обделяйте счастьем линуксоидов (и маководов))
- `.nojekyll` нужен чтобы GitHub Pages не выдавал 404 на файлы которые начинаются с _нижнего_подчёркивания
- Хочешь добавить что-то своё, добавляй в `sp_extra` - спец. папка контентов тех кто на посте ресурспакера
- Входная точка мода DynamicPack - файл `dynamicmcpack.repo.json` (v1 only)


## Я сделал изменения, как это всё запушить(?)
```
if были затронуты сплеши:
    splashes.py

sppack_auto.py -> 1 -> D // чтобы сделать весь json без pretty-print
sppack_auto.py -> 5
if выдало что какие-то картинки он исправил: // он всего лишь поменял размеры, текстуре ппц
    пиши разрабу пака, пускай чинят свои картинки
    
sppack_auto.py -> 6 // чтобы обновить renames.csv

if если я доделал v2 версию для dynamic_pack (always false hah):
    todo
    
// крч этот сценарий всегда true потому что v2 версию dynamicPack я не сделал
if для версии DynamicPack remote.type="dynamic_repo" (v1) :
    dynamicpack_auto.py -> 1 // ждём, он починит CRLF на LF и актуализирует в файлах метананных весь пак
    dynamicpack_auto.py -> 2 // он добавит +1 к номеру билда чтобы клиенты поняли что есть какие-то апдейты

всё коммитишь, как только изменения будут доступны на GitHub Pages нужный (а сейчас это акк Еврозда) то все клиенты DynamicPack скачают апдейт
```

## Dev/Prod
### PROD
На данный момент у всех игроков СП в ресурспаке лежит `dynamicmcpack.json` который ведёт на https://github.com/aladairmaxwell/SP

### DEV
Форк этого репо сейчас тут: https://github.com/AdamCalculator/SP_fork

Собстенно для разработки в файле `dynamicmcpack.json` внутри ВАШЕГО ЛОКАЛЬНОГО файла поменяйте ссылку на нужный GitHub Pages и ваш файл будет модом обновляться с вашего репозитория, а не с PROD

## Работники
- Enotis_
- Evrozd_
- AdamCalcualtor (current)

## Лицензия
(с) ВСЕ ПРАВА ЗАЩИЩЕНЫ

Данный пак лишь собирает воедино паки других авторов с их согласия.

Все данные о конкретном ресурспаке доступны в его папке в файле .packname_info.txt
