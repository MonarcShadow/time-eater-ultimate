# Acto 2 (Sonic moderno) — "Grieta del Tiempo"

> Estado: **fase B publicada** (2026-11-10, release 0.5.0: cielo, costuras y forma por sección; la caja gris fue la 0.4.x). Siguiente: fase C (piezas y enemigos reales). Slot: `bpc` (portal de Perfect Chaos), Sonic moderno.
> Generador: `niveles\grieta_del_tiempo\generar.py` · construir: `scripts\construir_nivel.ps1 -Nivel grieta_del_tiempo` · vistas de control: `niveles\comun\vista_previa.py`.
> Los nombres de objetos (`DashPanel`, `SszRollingFloor`…) son los reales del set data de cada zona: ver la tabla del final.

## La idea

El Time Eater no "ordena" las eras una detrás de otra: **las tritura y las cose mal**. Por eso el nivel no es una fila de zonas (Green Hill → Chemical Plant → …), sino un **collage**: en casi todos los tramos conviven 3 o 4 zonas a la vez, cada una aportando una **capa distinta**:

| Capa | Qué aporta | Ejemplo |
|---|---|---|
| **Suelo / estructura** | Por dónde corre Sonic | La tierra a cuadros de Green Hill |
| **Intrusión** | Geometría de otra era que atraviesa la primera | Tuberías de Chemical Plant que salen de la colina |
| **Gimmicks** | Mecánicas de una tercera zona | Plataformas giratorias de Sky Sanctuary |
| **Enemigos** | De una cuarta zona, fuera de lugar | Egg Fighters de Rooftop Run en una calle de City Escape |
| **Cielo** | Partido en dos, cambia sin aviso | Mitad día de Green Hill, mitad noche de Speed Highway |

### Tres reglas visuales que repiten el tema

1. **Costuras moradas.** Donde dos eras se tocan, la geometría no encaja: hay una franja de "tejido" morado (el color del Time Eater) con brillo, como una cicatriz. Es un material propio (`teu_costura`) que se reutiliza en todo el nivel y sirve para que el jugador lea "aquí se rompió el tiempo".
2. **Color comido.** Algunos trozos están **desteñidos**, en blanco y gris como el White Space: el Time Eater les quitó el color. Al principio son pocos; hacia el final casi todo está blanco. Técnicamente: copias de las texturas originales pasadas a escala de grises.
3. **El reloj que va hacia atrás.** Piezas de la torre del reloj de Rooftop Run aparecen en todo el nivel (una esfera en un acantilado, engranajes en una fábrica, una aguja clavada en el mar). Es el hilo conductor y el lugar del final.

### Progresión

El caos **crece**: el primer tramo mezcla 2–3 zonas y se entiende fácil; a la mitad hay 4 por tramo; el clímax junta **las 9 a la vez**; y el final es el silencio blanco.

Duración objetivo: **3–4 minutos**, unos 2,5 km, alternando boost en 3D, plataformas en 2D, quickstep, grind y un descenso en caída libre.

---

## Recorrido

```
 INICIO                                                                     META
   │                                                                          ▲
 [1] Colina contaminada ──► [2] Calle sobre las ruinas ──► [3] Mar en llamas │
                                                               │              │
                       ┌───────────────────────────────────────┘              │
                       ▼                                                      │
 [4] Fábrica dentro de la torre ──► [5] Rascacielos invertido ──► [6] Persecución
                                                                      │       │
                                       [8] Blanco ◄── [7] Caída de las 9 eras ┘
```

### 1. Colina contaminada (3D → 2D)  ·  Green Hill + Chemical Plant + Speed Highway

- **Ves:** arranca exactamente como Green Hill moderno (acantilados a cuadros, palmeras, el mar a la izquierda), pero del lado derecho la colina está **reventada por tuberías gigantes de Chemical Plant** que gotean Mega Mack morado y forman charcos sobre la hierba.
- **Cielo partido:** la mitad izquierda es el azul de Green Hill; la derecha, la noche con luces de Speed Highway. Cuando Sonic cruza la primera costura, el cielo cambia (`ChangeSkyCollision`).
- **Juego:** pista de boost con `DashPanel` y `DashRing`; el primer loop de Green Hill **atraviesa una tubería**: entras por la tierra, sales por el metal. Pasa a 2D (`ChangeMode_3Dto2D`) en un tramo de plataformas sobre los tubos, con un `CpzSewageTrap` (compuerta de Mega Mack) que se abre y se cierra.
- **Enemigos:** `EnemyMotora3D` (Moto Bug de Green Hill) y `EnemyLander` (Chemical Plant).
- **Reloj:** en la pared del acantilado hay una **esfera de reloj** de Rooftop Run, medio enterrada.

### 2. Calle sobre las ruinas (3D, quickstep)  ·  City Escape + Sky Sanctuary + Rooftop Run

- **Ves:** una calle cuesta abajo de City Escape (asfalto, semáforos, autos) que **flota en el cielo de Sky Sanctuary**: la calle se corta y los trozos de asfalto quedan como islas sobre las nubes, unidos por puentes de piedra de las ruinas.
- **Juego:** bajada a toda velocidad con quickstep entre dos carriles (uno de asfalto, otro de mármol); los tramos rotos se cruzan con `SszRollingFloor` (plataformas que ruedan) y nubes que rebotan (`SszCloud`). Hay `CtePhysicsCar` (autos que salen volando al tocarlos) **sobre las ruinas**.
- **Enemigos:** el ejemplo de la idea original, **plataformas de City Escape con enemigos de Rooftop Run**: `EnemyEFighter3D` y `EnemyEFighterSword3D` patrullando la calle, y `EnemyELauncher3D` disparando desde un balcón de Spagonia pegado a un edificio de City Escape.
- **Costura:** un edificio de City Escape está "cosido" a una torre de Sky Sanctuary a media altura; mitad ladrillo, mitad piedra blanca.

### 3. Mar en llamas (3D, agua/lava)  ·  Seaside Hill + Crisis City + Green Hill

- **Ves:** el mar de Seaside Hill, pero **algunas manchas del agua son lava de Crisis City**. Las boyas (`SshBuoy`) y las tortugas (`SshTurtle`) flotan tanto en agua como en lava. Al fondo, un tornado de Crisis City arrastra **pilares de las ruinas de Seaside Hill** y trozos de puentes de madera de Green Hill.
- **Juego:** correr sobre el agua con boost (como en Seaside Hill); las manchas de lava obligan a saltar o a usar quickstep. Un `CscLavaRide` (la roca que flota en la lava) cruza un tramo; luego un `Cannon` de Seaside Hill dispara a Sonic **a través del tornado** (`CscGenericTornado`) hacia la siguiente sección.
- **Enemigos:** `EnemyBiter3D` (Iblis de Crisis City) saltando del mar y `EnemyPawnLance3D` (Egg Pawn con lanza) sobre las ruinas.
- **Color comido:** los primeros trozos desteñidos aparecen aquí: unas columnas de Seaside Hill completamente blancas.

### 4. Fábrica dentro de la torre (2D principalmente)  ·  Planet Wisp + Rooftop Run + Chemical Plant

- **Ves:** el interior de la **torre del reloj de Rooftop Run**, pero en vez de engranajes de latón tiene la **maquinaria de la fábrica de Planet Wisp**: cintas, prensas y vagonetas, mezcladas con los engranajes del reloj. Por las ventanas se ve el cielo de Spagonia.
- **Juego:** sección vertical en 2D, subiendo. Las prensas del techo (`PlaBigPressCeling`) bajan **al ritmo de la campana del reloj**. Hay brazos cortadores (`PlaCutterArm`), sierras (`RollingSaw`), resortes y `WallJumpBlock` para trepar. En la mitad, un tramo de bloques giratorios de Chemical Plant (`CpzRotateBlocks`) dentro del mecanismo.
- **Enemigos:** `EnemyPawnPla2D` (Egg Pawn de Planet Wisp) y `EnemyGrabber2D` (la araña de Chemical Plant) colgando entre los engranajes.
- **Salida:** arriba del todo, Sonic sale por la esfera del reloj… directo a la noche de la sección 5.

### 5. Rascacielos invertido (3D → carrera por la pared)  ·  Speed Highway + Chemical Plant + Green Hill

- **Ves:** el famoso tramo de Speed Highway en el que Sonic **corre por la fachada de un rascacielos hacia abajo**, pero la fachada es la de un **tanque químico de Chemical Plant** y al pie del edificio no hay calle: hay una **cascada de Green Hill** que cae hacia arriba.
- **Juego:** cohete de Speed Highway (`SphRocket`) que lleva a Sonic hasta el edificio; bajada por la pared con `DashPanel`, esquivando ventanas que se rompen y reflectores (`SphSearchLight`) teñidos de morado. Abajo, un `Pulley` sube por la cascada invertida.
- **Enemigos:** `EnemyCopSpeeder3D` (los policías robot de Speed Highway) persiguiendo a Sonic **sobre puentes de madera de Green Hill** (`GhWoodBridge`), y `EnemySpinner`.

### 6. Persecución desincronizada (3D)  ·  City Escape + Rooftop Run + Sky Sanctuary + Seaside Hill

- **Ves:** el **camión de G.U.N. de City Escape** persigue a Sonic, pero no por una calle: por los **tejados de Spagonia**, que a su vez se desmoronan como los puentes de Sky Sanctuary. Al costado, el mar de Seaside Hill está a la altura de los tejados.
- **Juego:** set piece de persecución con el camión (`CteGunTruck200`); globos de fuego de Rooftop Run (`EucFireBalloon`) como plataformas para huir hacia arriba; tramos que colapsan (`SszCollapseTower`) mientras corres.
- **Enemigos:** `EnemyGunHunter3D` (City Escape) y `EnemyEFighter3D` (Rooftop Run) juntos en el mismo tejado.
- **Final del tramo:** el tejado se rompe bajo el camión y **Sonic cae**.

### 7. Caída de las 9 eras (caída libre)  ·  **las 9 zonas a la vez**

- **Ves:** Sonic cae por un **pozo enorme** cuyas paredes forman la **esfera de un reloj de 9 horas**: cada "hora" es un trozo de una zona distinta (Green Hill, Chemical Plant, Sky Sanctuary, Speed Highway, City Escape, Seaside Hill, Crisis City, Rooftop Run, Planet Wisp), y las 9 piezas **giran como manecillas en sentido contrario**.
- **Juego:** modo de caída libre (`ChangeDiveBegin` / `ChangeDiveEndNoEvent`, el mismo que usan Chemical Plant y Speed Highway): esquivar escombros de cada era y atravesar `DashRing` y `RainbowRing` en el centro del reloj.
- **Color comido:** a medida que se cae, las piezas pierden color; al fondo del pozo, todo es blanco.

### 8. Blanco (3D, final)  ·  White Space + todas, desteñidas

- **Ves:** Sonic aterriza en un trozo del **White Space** (`pam000`): todo blanco, silencioso. Alrededor flotan versiones **totalmente desteñidas** de piezas de las 9 zonas, quietas, como en el hub antes de rescatarlas. Tentáculos morados del Time Eater en el horizonte.
- **Juego:** una recta corta y tranquila con un último `RainbowRing`, un grind (`@GR`) sobre una aguja del reloj y el `GoalRing` frente a un **ojo** enorme en el cielo (el Time Eater mirando). Es el puente narrativo hacia el jefe nuevo.

---

## Qué zona aparece dónde

Ninguna zona va "en su turno": cada una aparece **varias veces, en capas distintas**.

| Zona | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Green Hill (ghz) | **suelo** | | fondo | | cascada, puentes | | ● | ● blanco |
| Chemical Plant (cpz) | tuberías, Mega Mack | | | bloques giratorios, araña | fachada | | ● | ● blanco |
| Sky Sanctuary (ssz) | | islas, plataformas | | | | tejados que colapsan | ● | ● blanco |
| Speed Highway (sph) | cielo nocturno | | | | **suelo**, cohete, policías | | ● | ● blanco |
| City Escape (cte) | | **suelo** (calle), autos | | | | camión G.U.N. | ● | ● blanco |
| Seaside Hill (ssh) | | | **suelo** (mar), boyas, cañón | | | mar a la altura | ● | ● blanco |
| Crisis City (csc) | | | lava, tornado, Iblis | | | | ● | ● blanco |
| Rooftop Run (euc) | esfera del reloj | Egg Fighters | | **la torre** | | **tejados**, globos | ● | aguja del reloj |
| Planet Wisp (pla) | | | | **fábrica**, prensas | | | ● | ● blanco |

---

## Cómo se construye (y qué tan difícil es)

**Geometría:** se extraen piezas del terreno de cada zona moderna (`Packed\<zona>200\Stage.pfd`) con HEIO o terrain2fbx, se acomodan en Blender junto a geometría propia (las costuras moradas, el pozo del reloj) y todo se convierte junto con Hedgehog Converter. Las versiones "comidas" son copias de las texturas en gris (texconv).

**Objetos, por nivel de riesgo:**

| Riesgo | Qué | Por qué |
|---|---|---|
| 🟢 Bajo | `Ring`, `DashPanel`, `DashRing`, `RainbowRing`, `Spring`, `WideSpring`, `JumpBoard3D`, `GrindDashPanel`, `Pulley`, `UpReel`, `WallJumpBlock`, `ChangeMode_*`, `GoalRing`, cámaras | Son comunes a todas las zonas |
| 🟡 Medio | Gimmicks y enemigos de otra zona (`SszRollingFloor`, `SszCloud`, `CpzRotateBlocks`, `SshBuoy`, `CscLavaRide`, `PlaBigPressCeling`, `EnemyEFighter3D`, `EnemyBiter3D`, `EnemyCopSpeeder3D`…) | Hay que copiar sus modelos, animaciones y colisiones al archivo del nivel. El Unleashed Project ya lo hizo con `SszRollingFloor`, `EucBird` y `CpzPipeEnterCollision` en su hub, así que es posible |
| 🔴 Alto | Set pieces: camión G.U.N. (`CteGunTruck200`), tornado (`CscGenericTornado`), cohete (`SphRocket`), caída libre (`ChangeDive*`), cielo que cambia (`ChangeSkyCollision`) | Dependen de varios objetos coordinados, eventos y parámetros propios de su escenario; hay que probarlos uno por uno |

**Orden de construcción propuesto:**
1. **Versión 0 (caja gris):** todo el recorrido con geometría simple en Blender + solo objetos 🟢. Sirve para ajustar ritmo, distancias y cámaras.
2. **Versión 1:** reemplazar la caja gris por piezas reales de las zonas (secciones 1, 2 y 3 primero) + costuras moradas.
3. **Versión 2:** enemigos y gimmicks 🟡, de uno en uno, publicando una release por cada grupo que funcione.
4. **Versión 3:** set pieces 🔴 (caída de las 9 eras primero, porque es el clímax).
5. **Versión 4:** color comido, iluminación (HedgeGI) y música.

---

## Inventario de objetos por zona (acto moderno, set data real)

Objetos más usados en `#<zona>200` (sin cámaras, anillos ni triggers internos):

- **Green Hill (ghz200):** DashPanel, GeneralFloor, Spring, DashRing, GrindDashPanel, EnemyMotora3D, EnemyBeeton2D/3D, ChangeMode_3Dto2D, GhzGiantBatabata, ChangeMode_3DtoDash, JumpPole, SlidingCollision, GhWoodBridge, UpReel, GhBreakCriff, EnemyGanigani2D/3D, AdlibTrickJump, WallJumpBlock, Pulley, ChangeSkyCollision.
- **Chemical Plant (cpz200):** CpzSewageTrap, EnemyLander2D/3D, CpzRotateBlocks, EnemyGrabber2D/3D, JumpBoard3D, Bomb, CpzBubble, CpzBigCrane, CpzPipe, CpzWaterCollision, ChangeDiveBegin, SelectCanon.
- **Sky Sanctuary (ssz200):** EnemyEggRobo2D/3D, SszCloud, SszRollingFloor, SszUpDownPole, SszBridge, SszWarpStart/Finish, SszCollapseTower, SszBreakFloor, SszDeathEggStar.
- **Speed Highway (sph200):** EnemyCopSpeeder2D/3D, SphGlassPillar, EnemySpinner, SphRollingLift, SphRocket, SphSearchLight, SphHelicopter, SphBell, SphHighWayCar, ChangeDiveBegin, RollingSaw.
- **City Escape (cte200):** CtePhysicsCar, CteHexagonFloor, EnemyGunHunter2D/3D, CteGunTruck200 (+ sus colisiones de ataque, deriva y salto), CteTrickJumpSkateBoard, EnemyMonoBeetle2D/3D, EnemyGunBeetle, IronPole2D, BoardGetOnOffCollision.
- **Seaside Hill (ssh200):** SshBuoy, SshRuinFloor, EnemyPawnLance2D/3D, EnemySpinner, Cannon, SshTurtle, ThornBall, SshGiantRock, EnemyPawn2D/3D, SshOrca, Fan, SshBobsleigh, EnemyPawnGun.
- **Crisis City (csc200):** CscIgnition, CscWindow, CscTornadoSwitch, EnemyTaker2D/3D, CscLavaRide, EnemyCrawler2D/3D, EnemyBiter2D/3D, CscBreakRoad, CscGenericTornado, CscFloatFloor.
- **Rooftop Run (euc200):** EucFireBalloon, EnemyEFighter2D/3D, EnemyEFighterSword2D/3D, Balloon, EnemyELauncher2D/3D, EucBird, EucGuillotine, Electric, EucPressThorn, EucAirShipChaser, EnemyEChaserManager, EnemyAeroCannon.
- **Planet Wisp (pla200):** PlaReleaseBox, PlaMissile, EnemyNal2D/3D, PlaHideFloor, EnemyPawnPla2D/3D, PlaBrokenCeling, PlaSetWisp, PlaShutter, PlaBigPressCeling, PlaTramCar, PlaCutterArm, RollingSaw, Flame, Cannon.
