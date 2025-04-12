## Описание
Простой rest сервис для добавления rest выключателя в homeassistant который будет выключать оповещения о событиях в tg из [ShinobiNVR](https://www.shinobi.video/)
## Применение
Написан для реализации сценария когда хочется оставить включенной запись событий, но при этом не присылать оповещения в TG. Например когда владелец находится дома и постоянное оповещение что обнаружен человек не нужны
Все что делает софтина - переключает настройку Send Telegram notifications. События сохраняются, но оповещения не приходят
# Использование
## Добавить контейнер с софтиной к контейнеру с HA
> [!IMPORTANT]
> Нужно чтобы в момент запуска HA сервис был уже запущен, поскольку если при старте проба не проходит то в дальнейшем HA не пытается попробовать снова самостоятельно

Пример docker-compose.yaml:
```
version: '3'
services:
  shinobi_proxy:
        image: 'nocrail/shinobi-ha-tg-switch:latest'
        container_name: shinobi_proxy
        restart: unless-stopped
        environment:
          SHINOBI_USERNAME: 'admin'
          SHINOBI_PASSWORD: 'admin'
          API_KEY: 'e0E6EEEeeeeE3eEeEefee2eeOeIE8e'
          API_GROUP: '2E2e2EEeEE'
          SHINOBI_URL: 'http://192.168.0.1:8080'
        ports:
            - '8085:8080'

  homeassistant:
    container_name: homeassistant
    image: ghcr.io/home-assistant/home-assistant:stable
    depends_on:
      - shinobi_proxy
    volumes:
      - ./config:/config
      - /etc/localtime:/etc/localtime:ro
      - /run/dbus:/run/dbus:ro
    restart: unless-stopped
    privileged: true
    network_mode: host
```

## Описание переменных

| Переменная  | Описание |
| ------------- | ------------- |
| SHINOBI_USERNAME  | Логин пользователя от Shinobi (не суперпользователь) от которого идет оповещение  |
| SHINOBI_PASSWORD  | Пароль пользователя от Shinobi (не суперпользователь) от которого идет оповещение  |
| API_KEY  | API ключ от того же пользователя [Как добыть](https://docs.shinobi.video/api/managing-api-keys-ui)  |
| API_GROUP  | Код группы от того же пользователя [Как добыть](https://docs.shinobi.video/api/managing-api-keys-ui)  |
| SHINOBI_URL  | Адрес сервера с Shinobi с протоколом и портом  |

## Добавление rest выключателя в HA
В файл configuration.yaml добавить код (с заменой URL и порта если необходимо)
```
switch:
  - platform: rest
    state_resource: http://192.168.0.1:8085/tg_state
    resource: http://192.168.0.1:8085/tg_toggle
    name: Shinobi_tg_switch
    is_on_template: "{{ value_json.is_active }}"
    body_on: '{"active": "true"}'
    body_off: '{"active": "false"}'
    headers:
      Content-Type: application/json
    verify_ssl: false
```

## Автоматизация
Я использую подобную автоматизацию, для выключения оповещений когда выключается сигнализация
```
alias: Снятие с охраны
description: ""
mode: single
triggers:
  - entity_id:
      - alarm_control_panel.ha_alarm
    to: disarmed
    trigger: state
conditions: []
actions:
  - data:
      message: |
        Охрана отключена 
    action: notify.Watchdog_grp
  - metadata: {}
    data: {}
    target:
      entity_id: switch.shinobi_tg_switch
    action: switch.turn_off
```
