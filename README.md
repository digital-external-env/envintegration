<div align="center">
  <a href="https://github.com/digital-external-env/envintegration">
    <img src="docs/images/main_logo.png" alt="Logo" width="60%" height="50%">
  </a>
</div>

## About

This library was created to develop solutions in the field of integrating the external environment of users into the ecosystem of their digital assistants. The library consists of several modules:
 * **pes_env** - for obtaining data on the psychoemotional state of the user from the physical environment
 * **pes_digenv** - for obtaining data on the psychoemotional state of the user from the digital environment
 * **env_manage** - for controlling the parameters of the external environment
 * **digital_hygiene** - for provide filtering of negative manifestations of the physical (projected) and digital external environment of users

## Built With

* [![Python][python-shield]][python-url]
* [![PDM][pdm-shield]][pdm-url]
* [![Google Fit][google-fit-shield]][google-fit-url]
* [![Yandex Smart Home][yandex-smart-home-shield]][yandex-smart-home-url]

## Requirements

* Python ~=3.10.6
* pip >=21.0 or PDM ~=2.4.2

## Getting started

### Prerequisites

[**env_manage**] Before you start, you need to register your application with
the [yandex authentication system](https://oauth.yandex.ru)
After that, using the received token, following
the [instruction](https://yandex.ru/dev/id/doc/dg/oauth/concepts/about.html), you need to get the client_token to work
with the API

[**pes_env**] Before you start, you also need to register your application with
the [google o2 authentication system](https://developers.google.com/identity/protocols/oauth2?hl=en). After that, using
the received token for `GoogleFitApi` using

### Installation

  ```sh
  pip install git+ssh://github.com/digital-external-env/envintegration.git
  ```
  or
  ```sh
  pdm add git+ssh://github.com/digital-external-env/envintegration.git
  ```

## How to Use

The Envintegration library provides a high-level API that allows you to use its capabilities in a simple way.

To use the API, follow these steps:

1. Import the module you need, for example:
```python
from envintegration import YandexApi
```
2. Сreate an instance of the Yandex API class by specifying in the client_token attribute a token received by
instructions
```python
api = YandexApi(client_token=client_token)
```
3. Usage instance:
```python
# Getting Smart Home Information
api.get_smart_home_info()
```
```python
# Getting device information and device management
my_purifer = api.purifer.set_id(device_id='')
my_purifer.info()
my_purifer.on_off(value=True)

my_vacuum_cleaner = api.purifer.set_id(device_id='')
my_vacuum_cleaner.get_capabilities()
my_vacuum_cleaner.mode(value='turbo')
```
For more details, see the [documentation](https://github.com/digital-external-env/envintegration/wiki)

## Examples

### env_manage
---

#### Getting Smart Home Information

```python
api.get_smart_home_info()
```

To simplify the operation, direct access to devices is implemented by creating an instance of the device class, and also
to methods available for devices, obtaining properties, abilities and information about the device.

(Note that all methods except set_id are asynchronous)

#### Getting device information and device management

```python
my_purifer = api.purifer.set_id(device_id='')
my_purifer.info()
my_purifer.on_off(value=True)

my_vacuum_cleaner = api.purifer.set_id(device_id='')
my_vacuum_cleaner.get_capabilities()
my_vacuum_cleaner.mode(value='turbo')

```

#### Create and execute scenario

```python
from asyncio import get_event_loop

loop = get_event_loop()

ys = YandexSessionAsync(login='login', password='password', station_id='3333333-0700-4e50-a82d-999d9999v9999')

loop.run_until_complete(ys.authorize())
loop.run_until_complete(ys.add_scenario(scenario_name='purifer',
                                        activation_command='purifer',
                                        instance='text_action',
                                        value='выключи очиститель воздуха'))
scenarios = loop.run_until_complete(ys.get_scenarios())
scenario_id = [scenario['id'] for scenario in scenarios if scenario['name'] == 'purifer'][0]
loop.run_until_complete(ys.exec_scenario(scenario_id=scenario_id))
loop.run_until_complete(ys.delete_scenario(scenario_id=scenario_id))
```

### pes_env
---
#### Get the number of steps that the user takes on walks

```python
steps_from_walks = loop.run_until_complete(GoogleFitApi.get_steps_from_walks())
```

#### Get user weight records

```python
weights = loop.run_until_complete(GoogleFitApi.get_weights())
```

#### Get user height records

```python
heights = loop.run_until_complete(GoogleFitApi.get_heights())
```

#### Get records of the user's sleep and their sleep phase at a certain time

The time range for searching for sleep and sleep phases is given by two numbers. The start time is unixSleepStartTime.
The end time is unixSleepEndTime. The time must be specified in Unix epoch data format.

```python
sleeps_and_phases_by_time = loop.run_until_complete(
    GFA.get_sleeps_and_phases_by_time(unixSleepStartTime[1], unixSleepEndTime[1]))
```

## Documentation

Also, a detailed Envintegration description is available in [GitHub Wiki](https://github.com/digital-external-env/envintegration/wiki)

## Acknowledgments

<div align="center">
  <a href="https://github.com/digital-external-env/envintegration">
    <img src="docs/images/logo.png" alt="Logo" width="30%" height="30%">
    <img src="docs/images/img.png" alt="Logo" width="30%" height="30%">
  </a>
</div>

### Affiliation

The library was developed in:

- [ITMO University](https://itmo.ru)
- [NCCR](https://actcognitive.org)

### Developers

- Oleg Basov - chief scientist
- Svetlana Roslyakova - scientist
- Anastasia Fedyanina - researcher
- Alina Remizova - researcher
- Yuliya Khlyupina - researcher
- Daria Klimova - researcher
- Anna Egamova - researcher
- Mikhail Sinko - ml-developer
- Valery Volokha - ml-developer
- Timur Samigulin - ml-developer
- Oleg Demin - ml-developer
- Tatiana Polonskaya - ml-developer
- Yuri Taran - backend-developer
- Andrew Laptev - backend-developer
- Denis Kuznetsov - backend-developer
- Danila Korobkov - backend-developer

### Contact

If you have any questions or comments on the project, email the developer - wvxp@mail.ru




<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[python-shield]: https://img.shields.io/badge/Python-%203.10-blue?style=for-the-badge&logo=python

[python-url]: https://www.python.org/downloads/release/python-310

[pdm-shield]: https://img.shields.io/badge/PDM-%202.4-purple?style=for-the-badge&logo=dpd

[pdm-url]: https://pdm.fming.dev/2.4

[google-fit-shield]: https://img.shields.io/badge/Google%20Fit-green?style=for-the-badge&logo=googlefit

[google-fit-url]: https://developers.google.com/fit/rest

[yandex-smart-home-shield]: https://img.shields.io/badge/Yandex%20Smart%20Home-red?style=for-the-badge&logo=data%3Aimage%2Fjpeg%3Bbase64%2C%2F9j%2F4AAQSkZJRgABAQAAAQABAAD%2F2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7%2F2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7%2FwAARCAAoACgDASIAAhEBAxEB%2F8QAGgAAAgMBAQAAAAAAAAAAAAAAAAgCBAUGA%2F%2FEADYQAAECAwQIAwUJAAAAAAAAAAIBAwAEEQUGEjEHExQVFiFBUTJhcSIjM0OBFzhSU3KFobHC%2F8QAGwEAAQUBAQAAAAAAAAAAAAAAAwACBAUHAQb%2FxAAmEQACAQMCBgIDAAAAAAAAAAABAgMABBEFEgYTIUFRcTFhkbHR%2F9oADAMBAAIRAxEAPwBw5%2Bcbk2kM0UiJcIAOZL2SKYSc5N%2B3PTBMivyGVpT1XrHkyDs6%2FNzjRgJtoTMqRjiEVRPEqcq8%2FwCIV5i%2Bd%2FtFmlKeW9bj1oBOuI5OtqXu5pvIXWVXkKoiURE5JTCvlGubpbfaWHQ9%2FFXmiaDLrHNWBxvUZCn5bzj1%2FPYanclnU%2BCVfxawq%2F3ECk5yT9uRmDeBM2HlrX0XpGXx5djgjjHejW59Xj13Wv5eHPHXlhzrC2v3zv7pT0pSK3UN%2BzwknFckm0L3cq3kTrypyJVTkqLVFrhTzbPeRxbQOpPwBRdJ4autQ5rtiNIwdzN0AI7e%2FwBfjLZWfONzjKmCKJCuEwLxCvZYIznAekZiUnHTAjcQWZogHCJKqeJEqtOfnlBErNeeqxdqm52u9Sr64ljD0nXEse%2Fd3zsy0w1bwVKUmxH25c%2B6d0XqOSp50WNmzy2O0X5E%2BQOkrrC965p9I1FyjjorqVYZBo1tcS2sqzQttZTkEUhnC1u8c%2FZ1tjev3ls%2BHWls%2BtpTWU%2FT1pWnKHG0YXEse4l3xs2zQ1jx0KbmyGjkwfdeyJ0HJE86rC6L97r9%2FwD8w3CZRUaVAis7Y6gkD1Wi8e6rcyxWsJbCvGrsB0yx7ms68dN0Od8Q4fXEkEQny2u0WJIOYNEjr69qeFPrBFzWaVcn5NucaQDVRIVqBjmK90imE5OSiYJ6XJ4E%2BeylUX1TNIIIVKuP4L0ecZcX7E9vraNp1utd%2BJSlcFafSkdgU5OTaYJGXJoFzfeSlPROsEEMRFXO0Yo891Ncbea5baMDJzgeB9Vcs%2BTbk2VAFUyJamZZkvdYIIIfQK%2F%2F2Q%3D%3D

[yandex-smart-home-url]: https://yandex.ru/dev/dialogs/smart-home/doc/concepts/platform-quickstart.html
