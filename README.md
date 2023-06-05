## Тесты

В репозитории находится два тестовых проекта.
Использованы две различные библиотеки для тестирования.

| Проект | Тесты |
| ------ | ------ |
| YaNote | unittest |
| YaNews | pytest |

Не забудьте установить виртуальное окружение и зависимости

Чтобы запустить YaNote или YaNews нужно выполнить команду

```sh
python manage.py runserver
```




Чтобы запусутить тесты в YaNote нужно выполнить команду
```sh
python manage.py test
```
Можно использовать различные ключи запуска, например
```sh
python manage.py test -v2
```
Он даст более подробный отчет


Для запуска тестов YaNews выполните команду
```sh
pytest
```
Также применимы ключи ```-v``` или ```-vv```
