# Changelog

## 0.6.0
- **Nivel laboratorio** en el portal del rival **Shadow**: una pista recta de 170 m para probar cosas arriesgadas sin tocar Grieta del Tiempo.
- Primer experimento: dos **Egg Fighters de Rooftop Run** (a 45 m y 70 m del inicio). Para cargarlos, el escenario se añade al árbol de enemigos del juego.
- Si el laboratorio cierra el juego, basta con no entrar a ese portal; el resto del mod no cambia.

## 0.5.1
- El planeo termina más abajo, a unos 10 m del suelo.
- Segunda rampa con el mismo impulso con y sin boost (antes con boost se pasaba del resorte).
- Aro de impulso de prueba girado: ahora debe lanzar hacia la meta.

## 0.5.0
Grieta del Tiempo, fase B: las 8 secciones con más forma.
- **Cielo**: el de Perfect Chaos en lugar del fondo negro.
- **Costuras moradas** (franja y dos postes) en cada unión entre secciones.
- S1: acantilados de Green Hill, tuberías de Chemical Plant que cruzan sobre la pista, un tanque y charcos de Mega Mack.
- S2: fachadas de City Escape a ambos lados, rematadas con trozos de ruina de Sky Sanctuary; columnas y asfalto desprendido en las islas.
- S3: el mar alrededor de la pista, **manchas de lava que hacen daño**, pilares (uno ya sin color) y un tornado.
- S4: la pared de la torre sigue toda la escalera y lleva engranajes.
- S5: ventanas iluminadas, tanques y agua en la cascada.
- S6: casas vecinas y chimeneas en los tejados.
- S7: escombros repartidos para el planeo lento y anillos en espiral.
- S8: explanada blanca más ancha, columnas desteñidas, aguja más larga y el ojo del Time Eater como disco.
- Prueba: un aro de impulso (DashRing) cerca de la meta, para comprobar su orientación.

## 0.4.3
- Planeo más lento en el pozo (parámetros de Sonic propios del nivel): la caída dura unos 6 s en vez de menos de 3.
- Primera rampa con un poco más de impulso, para aterrizar encima de la isla.
- Meta más alta: ya no queda parcialmente bajo el suelo.

## 0.4.2
- Arreglo del cierre del juego al entrar en la caída de planeo: el escenario ahora carga las animaciones de planeo de Sonic (`SonicDiving`), que el juego solo cargaba en Chemical Plant, Speed Highway, Planet Wisp y el Egg Dragoon.
- Primera rampa (sección 2): más impulso y ángulo empinado. Segunda rampa (sección 3): más impulso.
- Meta de vuelta a su altura original (se mantiene en vertical).

## 0.4.1
Correcciones de Grieta del Tiempo tras la primera prueba:
- Rampas de salto giradas 180° (ahora lanzan hacia adelante) y meta en vertical.
- Paneles de impulso inclinados según la pendiente del suelo.
- Curvas sin paneles, más abiertas y con muro exterior de 3 m.
- Resorte del escalón (sección 5) y último resorte de la torre con más fuerza.
- Cambios a 2D y de vuelta a 3D lejos de los precipicios.
- Riel de grind visible bajo los pies de Sonic.
- Pozo final: la entrada es un agujero en una explanada, con un tejado largo antes para frenar, y se añade la zona de planeo (caída libre).

## 0.4.0
- **Grieta del Tiempo v0 (caja gris)** en el portal de Perfect Chaos (Acto 2, Sonic moderno): el recorrido completo de las 8 secciones del diseño con geometría simple (~1,4 km). Los bloques de colores marcan qué zona aporta cada pieza.
  1. Colina contaminada (3D + plataformas en 2D) · 2. Calle sobre las ruinas (quickstep cuesta abajo + rampa a islas flotantes) · 3. Mar en llamas (pista ancha en curva + rampa) · 4. Fábrica dentro de la torre (subida en 2D con resortes) · 5. Rascacielos invertido (bajada empinada + escalón con resorte) · 6. Persecución (tejados con huecos + riel de grind) · 7. Caída de las 9 eras (pozo de 110 m) · 8. Blanco (riel corto y meta).
- Solo objetos básicos (anillos, paneles de impulso, resortes, rampas, cambios a 2D/quickstep, meta). Enemigos y gimmicks de cada zona llegan en próximas versiones.

## 0.3.0
- Nivel de prueba moderno en el portal de **Perfect Chaos** (Acto 2, Sonic moderno): un camino recto de 130 m en 3D con dos paneles de impulso, anillos y la meta (GoalRing) a 100 m.
- El nivel de prueba del Death Egg Robot (Acto 1) se mantiene igual (probado: se puede completar, la meta y la puntuación funcionan).

## 0.2.0
- Nivel de prueba "solo un camino" en el portal del **Death Egg Robot** (Acto 1, Sonic clásico): un camino recto de 40 m con 5 anillos y la meta a 25 m del inicio.
- Es una prueba técnica de todo el proceso (Blender → Hedgehog Converter → Havok Converter → juego). El modo difícil del Death Egg Robot sigue siendo el jefe original.

## 0.1.2
- Las actualizaciones ahora se sirven desde la rama `hmm-update` (compatible con Hedge Mod Manager 7.15 y 8).

## 0.1.1
- Versión de prueba para verificar las actualizaciones desde Hedge Mod Manager.

## 0.1.0
- Reinicio del proyecto desde cero (el trabajo anterior está en `legacy/` del repositorio).
- Estructura base del mod y actualizaciones automáticas desde GitHub Releases.
