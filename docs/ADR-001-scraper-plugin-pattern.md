# ADR-001: Plugin Pattern (Registry) para Scrapers

**Estado:** Aceptado  
**Fecha:** 2024-11-08  
**Afecta a:** `backend/app/scrapers/registry.py`, `backend/app/scrapers/base.py`, `backend/app/core/orchestrator.py`

---

## Contexto

PeopleDoxx necesita consultar múltiples fuentes de datos gubernamentales ecuatorianas. El número de fuentes puede crecer con el tiempo (SRI, SATJE, SUPA, IESS, CNE, MDT, etc.) y la comunidad open-source puede querer contribuir nuevos scrapers sin modificar el núcleo del sistema.

El riesgo principal es el **acoplamiento**: si el `Orchestrator` importa y llama explícitamente a cada scraper, agregar uno nuevo requiere modificar el orquestador (viola OCP).

---

## Decisión

Implementar un **Registry Pattern** combinado con un **decorador de registro automático**:

```python
# En registry.py
class ScraperRegistry:
    _scrapers: dict[str, type[BaseScraper]] = {}

    @classmethod
    def register(cls, scraper_cls: type[BaseScraper]) -> type[BaseScraper]:
        cls._scrapers[scraper_cls.SOURCE_ID] = scraper_cls
        return scraper_cls

# En sri.py — el scraper se auto-registra al importarse
@ScraperRegistry.register
class SriScraper(BaseScraper):
    SOURCE_ID = "SRI"
    ...
```

Los scrapers se importan en `app/scrapers/__init__.py` para garantizar que el decorador se ejecute al iniciar la aplicación. El `Orchestrator` llama a `ScraperRegistry.get_all()` y ejecuta todos concurrentemente con `asyncio.gather`.

---

## Alternativas descartadas

| Alternativa | Razón del descarte |
|---|---|
| Lista hardcoded de scrapers en Orchestrator | Viola OCP — cada nuevo scraper exige modificar el orquestador |
| Descubrimiento dinámico por filesystem (`importlib`) | Mayor complejidad, difícil de testear, riesgo de importar módulos inesperados |
| Inyección de dependencias con contenedor IoC (dependency-injector) | Sobrediseño para la escala actual; registry es suficiente y más simple |

---

## Consecuencias

- Ventaja: Agregar una nueva fuente = crear un archivo en `/scrapers/`, decorar con `@ScraperRegistry.register`, e importarlo en `__init__.py`. Nada más.  
- Ventaja: Tests unitarios pueden mockear el registry limpiamente.  
- Precaución: Si el número de scrapers supera 20–30 y el registry en memoria se vuelve un bottleneck, considerar migrar a un sistema de plugins basado en `entry_points` de setuptools.

---

## Se revisa si

- El número de scrapers activos supera 20 y se observa degradación de rendimiento en la inicialización.
- Se necesita carga/descarga dinámica de scrapers sin reiniciar el proceso (hot reload).

