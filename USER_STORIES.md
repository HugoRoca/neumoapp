# Historias de usuario — Neumoapp

Documento de producto al estilo **Product Owner**: épicas, historias de usuario, valor de negocio, criterios de aceptación y trazabilidad respecto a la planificación de sprints (`clientSide/SPRINT_PLANNING.md`, `service/SPRINT_PLANNING.md`).

**Versión:** 1.1  
**Producto:** aplicación web para gestión de citas médicas en contexto multi-hospital (cliente React + API FastAPI + PostgreSQL), con **asistente conversacional** basado en modelo de lenguaje y herramientas de negocio en servidor.

---

## 1. Visión y alcance del producto

### 1.1 Visión

Neumoapp permite a los **pacientes** autenticados **reservar, consultar, cancelar y reagendar** citas médicas siguiendo una jerarquía clara: **Hospital → Especialidad → Consultorio**, con **franjas horarias generadas dinámicamente** (slots) y reglas de negocio que evitan solapes y combinaciones inválidas. Opcionalmente, el mismo paciente puede usar un **asistente de IA** que interpreta lenguaje natural y, mediante **herramientas seguras** en el backend, consulta reglas de agenda, listados y operaciones de citas **con la misma validez** que el resto de la API (JWT, validaciones de dominio).

### 1.2 Personas

| Persona | Descripción | Necesidades principales |
|--------|-------------|-------------------------|
| **Paciente** | Usuario final de la aplicación web | Acceso seguro, claridad en el flujo de reserva (formulario o asistente), visibilidad de sus citas y control sobre cancelación/reagendamiento |
| **Equipo de producto / PO** | Define prioridades y criterios de éxito | Historias priorizables, criterios verificables, alineación con arquitectura Hospital–Especialidad–Consultorio |
| **Equipo técnico** | Frontend, backend, datos | Contratos de API claros, estados de cita coherentes, manejo de zonas horarias y feriados |

### 1.3 Fuera de alcance (según SPRINT_PLANNING y producto)

- Tests automatizados exhaustivos (marcados como mejora futura en cliente).
- Internacionalización (i18n), notificaciones push, exportación a calendarios externos (mejoras futuras).
- **Diagnóstico o consejo médico** por parte del asistente: el producto orienta la **gestión administrativa de citas**, no la práctica clínica.

El **asistente de IA** está descrito en la **Épica F**; su implementación vive en `clientSide/src/pages/ChatAssistant.jsx`, `clientSide/src/services/chat.service.js`, `service/app/services/openai_chat_service.py` y `service/app/services/chat_tool_executor.py`.

### 1.4 Principios de diseño reflejados en las historias

- **Seguridad de acceso:** rutas privadas y sesión coherente con JWT.
- **Jerarquía explícita:** no se agenda sin validar hospital, especialidad y consultorio compatibles.
- **Transparencia de disponibilidad:** el paciente ve franjas acordes a turno y fecha; el sistema no permite reservas en slots inválidos u ocupados (validación en backend).
- **Experiencia responsive:** uso razonable en móvil y escritorio.
- **Asistente de IA:** toda acción sobre citas pasa por **herramientas** validadas en servidor (listar hospitales/especialidades/consultorios, reglas de agenda, crear/actualizar/eliminar citas, listar citas); el modelo **no** sustituye las validaciones de negocio ni el criterio profesional sanitario.
- **Configuración del modelo:** soporte de proveedor en la nube (p. ej. OpenAI) o local (p. ej. Ollama/LM Studio) mediante variables de entorno del servicio, con tiempos de respuesta variables en entornos locales.

---

## 2. Mapa de épicas e historias

| Épica | ID historias | Objetivo de la épica |
|-------|----------------|----------------------|
| A. Cuenta y acceso | US-01 — US-02 | Entrar y salir del sistema de forma segura y predecible |
| B. Panel y visión de citas | US-03 | Ver de un vistazo las próximas citas |
| C. Reserva guiada | US-04 — US-08 | Completar una reserva con datos correctos y confirmación |
| D. Gestión de citas | US-09 — US-11 | Listar, cancelar y reagendar citas existentes |
| E. Experiencia transversal | US-12 | Calidad de uso en distintos dispositivos |
| F. Asistente de IA | US-13 — US-18 | Gestionar citas y consultas en lenguaje natural con flujo guiado y respaldo del backend |

**Priorización sugerida (MVP):** A → B → C → D, con E aplicada de forma continua. **F** puede desarrollarse en paralelo una vez existan autenticación y endpoints de citas/hospitales/slots, o entregarse como incremento posterior al flujo por formulario.

---

## 3. Épica A — Cuenta y acceso

### Contexto de la épica

Sin autenticación fiable no hay trazabilidad de citas por paciente. Esta épica cubre registro/login, persistencia de sesión según el diseño acordado (p. ej. almacenamiento de token), interceptores HTTP y **protección de rutas** para que solo usuarios autenticados accedan al panel y a la gestión de citas.

**Dependencias técnicas (backend):** endpoints de autenticación (`/auth/register`, `/auth/login`, `/auth/me` o equivalentes documentados en la API).

**Riesgos si falla:** fugas de rutas privadas, tokens mal gestionados, mala experiencia al expirar sesión.

---

### US-01 — Registro e inicio de sesión

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **Quiero** | registrarme e iniciar sesión en la aplicación |
| **Para** | acceder a mis citas y al flujo de reserva de forma identificada |

**Valor de negocio:** habilita el modelo multi-usuario y el vínculo entre identidad y citas en base de datos.

**Descripción ampliada**

- El flujo de registro debe solicitar los datos mínimos acordados con el backend (validación alineada con Pydantic en API).
- El login debe intercambiar credenciales por un token JWT (o mecanismo definido en API) y propagar el estado de “usuario autenticado” a la aplicación (p. ej. React Context).
- Los errores de credenciales o validación deben mostrarse de forma legible, sin filtrar detalles internos del servidor.

**Criterios de aceptación**

1. Dado un usuario no registrado, cuando completa el registro con datos válidos, entonces se crea la cuenta y puede iniciar sesión (o se le indica el siguiente paso según flujo definido).
2. Dado un usuario registrado, cuando introduce credenciales correctas, entonces obtiene sesión autenticada y accede al área privada.
3. Dado credenciales incorrectas, cuando intenta iniciar sesión, entonces ve un mensaje de error claro y no accede al área privada.
4. Los campos obligatorios y formatos (email, contraseña, etc.) están validados en cliente de acuerdo con las reglas de la API.

**Notas técnicas:** cliente Axios, servicio `auth.service.js`, `AuthContext`; alineación con `SPRINT_PLANNING` cliente (T1.3).

---

### US-02 — Sesión persistente y rutas protegidas

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **Quiero** | que mi sesión se mantenga de forma acordada y que las páginas privadas estén protegidas |
| **Para** | no tener que repetir login en cada acción y evitar que otros accedan a mis datos sin autenticación |

**Valor de negocio:** reduce fricción y refuerza la confianza en el producto.

**Descripción ampliada**

- Tras el login, el token (u otra señal de sesión) se almacena según decisión de diseño (p. ej. `localStorage`) y los interceptores de Axios adjuntan el header de autorización.
- Las rutas del panel, reserva e historial de citas deben exigir autenticación; el visitante anónimo es redirigido al login.
- El cierre de sesión debe limpiar el estado local y bloquear el acceso a rutas privadas hasta un nuevo login.

**Criterios de aceptación**

1. Dado un usuario autenticado, cuando recarga la página, entonces la sesión se recupera sin obligar a login de nuevo (salvo expiración de token según política del backend).
2. Dado un usuario no autenticado, cuando intenta abrir una URL privada, entonces es redirigido al login.
3. Dado un usuario autenticado, cuando usa “Cerrar sesión”, entonces pierde el acceso al área privada hasta volver a autenticarse.
4. Las llamadas a API desde el área privada incluyen el mecanismo de autorización esperado por el backend.

**Notas técnicas:** `ProtectedRoute`, React Router, interceptores JWT (`SPRINT_PLANNING` cliente T1.2, T1.4).

---

## 4. Épica B — Panel y visión de citas

### Contexto de la épica

El paciente necesita **contexto inmediato** sobre sus próximas obligaciones sanitarias. El panel resume citas venideras sin sustituir la vista detallada del historial.

**Dependencias:** endpoints de citas próximas (`/appointments/upcoming` o equivalente), hooks y servicios de citas.

---

### US-03 — Próximas citas en el panel principal

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **Quiero** | ver un resumen de mis próximas citas en el panel principal |
| **Para** | planificar mi asistencia sin buscar en el historial completo |

**Valor de negocio:** aumenta la retención y reduce llamadas de recordatorio si en el futuro se añaden notificaciones.

**Descripción ampliada**

- El panel muestra un número limitado de próximas citas (según acuerdo de producto, p. ej. hasta cinco), ordenadas cronológicamente.
- Cada ítem debe mostrar al menos: fecha, hora, especialidad (y hospital si el modelo de datos lo expone de forma útil).
- Deben contemplarse estados de **carga**, **vacío** (“no tienes próximas citas”) y **error** (fallo de red o servidor).

**Criterios de aceptación**

1. Dado un paciente con próximas citas, cuando abre el panel, entonces ve una lista acotada de citas futuras con la información acordada.
2. Dado un paciente sin citas futuras, cuando abre el panel, entonces ve un mensaje o estado vacío explícito.
3. Dado un fallo de API, cuando el panel intenta cargar datos, entonces el usuario ve un mensaje de error comprensible y opción de reintentar si el diseño lo incluye.
4. El diseño es coherente con el sistema de diseño (componentes base, tipografía, espaciado).

**Notas técnicas:** `Dashboard.jsx`, `useUpcomingAppointments`, `appointment.service.js` (`SPRINT_PLANNING` cliente T2.5).

---

## 5. Épica C — Reserva guiada (Hospital → Especialidad → Consultorio)

### Contexto de la épica

Esta es la épica central del producto según el backend: **arquitectura jerárquica** Hospital → Especialidades → Consultorios, **slots dinámicos** (sin tabla de horarios pregenerada), validación de disponibilidad y reglas de turno (mañana/tarde). El frontend debe guiar al paciente paso a paso y sincronizar con los endpoints de hospitales, especialidades, consultorios y slots.

**Dependencias:**  
`/hospitals/`, `/hospitals/{id}/specialties`, `/consultation-rooms/by-hospital-and-specialty`, `/slots/available`, `POST /appointments/`.

**Riesgos si falla:** combinaciones inválidas en UI que el backend rechaza; problemas de zona horaria en fechas; confusión entre franjas ocupadas y libres.

---

### US-04 — Seleccionar hospital y especialidad

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **Quiero** | elegir primero el hospital y después la especialidad médica |
| **Para** | acotar la oferta al centro que ofrece el servicio que necesito |

**Valor de negocio:** refleja el modelo multi-hospital real y evita citas en especialidades no prestadas en ese centro.

**Descripción ampliada**

- El listado de hospitales proviene de la API; al seleccionar un hospital, las especialidades mostradas deben ser solo las asociadas a ese hospital.
- Cambiar de hospital debe resetear o invalidar selecciones posteriores (especialidad, consultorio, fecha, hora) para no enviar combinaciones inconsistentes.
- La UI debe indicar en qué paso del asistente de reserva se encuentra el usuario (indicadores visuales multi-step).

**Criterios de aceptación**

1. Dado el inicio del flujo de reserva, cuando elijo un hospital, entonces solo puedo seleccionar especialidades vinculadas a ese hospital.
2. Dado un cambio de hospital después de avanzar, cuando confirmo el cambio, entonces las selecciones dependientes se resetean o se validan de nuevo.
3. Los errores de API (hospital o especialidad no encontrados) se muestran sin romper el flujo completo.

**Trazabilidad:** `service/SPRINT_PLANNING` T2.1, T2.3; cliente T3.1.

---

### US-05 — Seleccionar consultorio y turno

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **Quiero** | elegir consultorio y turno (mañana o tarde) |
| **Para** | acotar el lugar físico y la franja del día en la que puedo ser atendido |

**Valor de negocio:** conecta la oferta real de cada consultorio con la generación de slots por reglas de negocio.

**Descripción ampliada**

- Los consultorios se filtran por **hospital y especialidad** (endpoint dedicado).
- El turno (mañana/tarde) condiciona el rango horario que usa el backend para generar slots (p. ej. ventanas definidas en `SlotService`).
- Solo deben mostrarse consultorios activos según las reglas del backend.

**Criterios de aceptación**

1. Dado hospital y especialidad seleccionados, cuando pido consultorios, entonces la lista corresponde a esa combinación.
2. Dado un consultorio elegido, cuando selecciono turno, entonces las peticiones posteriores de slots usan fecha, turno, hospital, especialidad y consultorio coherentes.
3. Si no hay consultorios para la combinación, el usuario recibe un mensaje claro (alineado con respuestas 404 o vacías de la API).

**Trazabilidad:** backend T1.2, T2.2, T2.5; cliente T3.1.

---

### US-06 — Seleccionar fecha en calendario

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **Quiero** | elegir una fecha en un calendario interactivo |
| **Para** | reservar solo en días hábiles y permitidos por la política del sistema |

**Valor de negocio:** reduce errores de entrada y alinea la UX con feriados y días no laborables.

**Descripción ampliada**

- Fechas pasadas deshabilitadas.
- Fines de semana deshabilitados (según reglas del proyecto).
- Feriados según lista configurada (p. ej. feriados locales en constantes del cliente).
- Tooltips o leyenda para feriados.
- Normalización de fechas para evitar desfaces por zona horaria (requisito explícito en la planificación del cliente).

**Criterios de aceptación**

1. No puedo seleccionar fechas anteriores al día actual (según regla de negocio acordada).
2. No puedo seleccionar sábados ni domingos.
3. Los feriados definidos en configuración aparecen no seleccionables y, si aplica, con indicación visual.
4. La fecha enviada a la API de slots es coherente con la fecha mostrada al usuario (sin “día corrido” por UTC).

**Trazabilidad:** cliente T3.2, T4.5 (refinamiento timezone); `holidays.js`.

---

### US-07 — Seleccionar horario (slot) disponible

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **Quiero** | ver las franjas horarias disponibles y elegir una |
| **Para** | completar mi reserva en un hueco realmente libre |

**Valor de negocio:** núcleo de la promesa del sistema; depende de la generación dinámica de slots y del estado de ocupación.

**Descripción ampliada**

- Llamada al endpoint de slots con los parámetros requeridos (hospital, especialidad, consultorio, fecha, turno, etc., según contrato API).
- Si la API devuelve slots con bandera `available`, la UI debe distinguir visualmente ocupado vs libre cuando el producto lo requiera.
- Al cambiar fecha o turno, se deben refrescar los slots y limpiar la selección previa de hora si deja de ser válida.

**Criterios de aceptación**

1. Dado un día y turno válidos, cuando se cargan slots, entonces el usuario ve las franjas pertinentes y solo puede confirmar una franja permitida.
2. Dado un cambio de fecha o turno, cuando los slots se recalculan, entonces no queda seleccionada una hora incompatible.
3. Dado un fallo de red, cuando falla la carga de slots, entonces el usuario puede reintentar o volver atrás sin perder el contexto mínimo del flujo.

**Trazabilidad:** backend T1.1, T2.4; cliente T3.3.

---

### US-08 — Motivo de consulta, validación y confirmación de cita

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **quiero** | indicar el motivo de consulta, revisar el resumen y confirmar |
| **Para** | asegurarme de que la información enviada al hospital es correcta antes de crear la cita |

**Valor de negocio:** reduce errores clínicos-administrativos y mejora la trazabilidad del motivo de la visita.

**Descripción ampliada**

- Campo de motivo de consulta con validación (longitud mínima/máxima según API).
- Al enviar, se llama a `POST /appointments/` con el payload acordado.
- Modal o paso de **confirmación** previa que muestre hospital, especialidad, consultorio, fecha, hora y motivo (patrón distinto para cita nueva vs reagendamiento — ver US-11).
- Tras éxito: mensaje de confirmación y redirección al panel u otra pantalla definida por UX.
- Errores del servidor (slot ya tomado, validación de negocio) deben mostrarse de forma accionable.

**Criterios de aceptación**

1. No puedo enviar la cita sin completar los campos obligatorios validados en cliente.
2. Antes de crear la cita, cuando el flujo lo define, veo un resumen claro y debo confirmar explícitamente.
3. Dado una creación exitosa, cuando termina el flujo, entonces soy llevado al destino acordado y veo feedback de éxito.
4. Dado un error de negocio del backend, cuando falla el POST, entonces entiendo la causa o el siguiente paso (sin datos sensibles del servidor).

**Trazabilidad:** cliente T3.4, T4.4; backend T1.3, T2.3.

---

## 6. Épica D — Gestión de citas existentes

### Contexto de la épica

Tras reservar, el paciente debe **ver el conjunto de citas**, **cancelar** cuando no pueda asistir y **reagendar** manteniendo coherencia de estados (incluido el estado `rescheduled` en backend). Esta épica cierra el ciclo de vida de la cita en el producto MVP.

**Dependencias:** listado de citas del usuario, `DELETE` y lógica de actualización/reagendamiento (`PATCH` según planificación cliente).

---

### US-09 — Ver todas mis citas

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **Quiero** | ver un listado de todas mis citas |
| **Para** | revisar fechas, horas, especialidades y estados en un solo lugar |

**Valor de negocio:** transparencia y autonomía del paciente.

**Descripción ampliada**

- Vista dedicada (p. ej. `MyAppointments.jsx`) con listado responsive.
- Cada ítem muestra información suficiente para decidir cancelar o reagendar (fecha, hora, especialidad, estado, hospital si aplica).
- Estados vacíos y errores tratados de forma equivalente al panel.

**Criterios de aceptación**

1. Dado un paciente con citas, cuando abre el listado, entonces ve todas las citas retornadas por la API para su usuario.
2. Dado un paciente sin citas, cuando abre el listado, entonces ve un estado vacío claro.
3. La información mostrada es coherente con los datos del backend (incluyendo estados: pendiente, confirmada, cancelada, reagendada, según modelo).

**Trazabilidad:** cliente T4.1; endpoint `/appointments/my-appointments` o equivalente.

---

### US-10 — Cancelar una cita

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **Quiero** | cancelar una cita que ya no podré atender |
| **Para** | liberar el cupo y mantener mi historial alineado con la realidad |

**Valor de negocio:** mejor uso de capacidad instalada y menos inasistencias no comunicadas.

**Descripción ampliada**

- Acción explícita “Anular” o equivalente en cada cita cancelable según reglas de negocio (p. ej. no cancelar citas pasadas si así lo define el producto).
- **Diálogo de confirmación** reutilizable para evitar cancelaciones accidentales.
- Tras confirmar, llamada a API de borrado/cancelación y actualización optimista o refresco del listado.
- Feedback de éxito o error.

**Criterios de aceptación**

1. Dado una cita cancelable, cuando solicito cancelar, entonces debo confirmar en un diálogo antes de ejecutar la acción.
2. Dado una cancelación exitosa, cuando vuelvo al listado o panel, entonces el estado de la cita refleja la cancelación.
3. Dado un error de servidor, cuando falla la cancelación, entonces el usuario es informado y la UI no asume éxito.

**Trazabilidad:** cliente T4.2; `DELETE /appointments/{id}` según dependencias documentadas.

---

### US-11 — Reagendar una cita

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **Quiero** | cambiar la fecha y/u hora de una cita existente mediante un flujo guiado |
| **Para** | mantener la cita activa en un nuevo slot sin duplicar reservas incorrectamente |

**Valor de negocio:** flexibilidad para el paciente y mejor ocupación de agenda.

**Descripción ampliada**

- Desde el listado, acción “Reagendar” que abre el flujo de reserva en **modo reagendamiento** con datos de la cita original precargados o referenciados.
- El sistema debe reflejar el estado **reagendada** en la cita origen según reglas del backend (`AppointmentStatus.RESCHEDULED`, slots ocupados correctamente).
- El diálogo de confirmación debe diferenciar mensajes de **cita nueva** vs **reagendamiento** (según `SPRINT_PLANNING` cliente T4.3, T4.4).
- No debe quedar una doble reserva activa incoherente tras completar el flujo.

**Criterios de aceptación**

1. Dado una cita elegible para reagendamiento, cuando inicio el flujo, entonces reconozco que estoy reagendando (copys y/o datos de referencia visibles).
2. Dado un reagendamiento completado con éxito, cuando consulto el listado, entonces la nueva cita aparece y la cita original queda en el estado definido por negocio (p. ej. `rescheduled`).
3. Dado un fallo a mitad del flujo, entonces no se deja el sistema en un estado inconsistente sin posibilidad de recuperación (mensajes claros).
4. El backend rechaza combinaciones inválidas (misma validación que una reserva nueva).

**Trazabilidad:** backend T2.6; cliente T4.3; endpoints `PATCH`/`DELETE` según matriz de dependencias del cliente.

---

## 7. Épica E — Experiencia transversal (UX / responsive)

### Contexto de la épica

No es una funcionalidad aislada sino un **requisito transversal**: formularios largos, calendario y listas deben ser usables en pantallas pequeñas y grandes.

---

### US-12 — Usar la aplicación en móvil y escritorio

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **Quiero** | usar la aplicación con una interfaz usable en móvil y en escritorio |
| **Para** | gestionar mis citas desde el dispositivo que tenga disponible |

**Valor de negocio:** accesibilidad práctica y mayor tasa de finalización del flujo de reserva.

**Descripción ampliada**

- Layout principal con navegación adaptable (p. ej. menú hamburguesa en móvil).
- Formularios multi-step legibles sin scroll excesivo innecesario; botones alcanzables.
- Tablas o listas que no rompan el diseño en anchos estrechos.

**Criterios de aceptación**

1. Las vistas principales (login, panel, reserva, mis citas) son usables en un ancho representativo de móvil sin solapamiento crítico de controles.
2. La navegación principal es accesible desde layouts definidos (`Navbar`, `MainLayout`).
3. No se exige scroll horizontal para completar los pasos críticos del flujo de reserva en viewports definidos por el equipo (definir breakpoints de prueba en validación manual).

**Trazabilidad:** cliente T2.2, T4.5, criterios globales de Sprint 1 y 2.

---

## 8. Épica F — Asistente de IA para gestión de citas

### Contexto de la épica

El asistente permite al paciente **hablar con lenguaje natural** (“quiero cita mañana por la mañana”, “¿qué citas tengo?”, “cancelar la del jueves”) sin recorrer obligatoriamente el formulario multi-paso. En el **servidor**, un modelo de lenguaje (OpenAI en la nube o compatible vía `OPENAI_BASE_URL`, p. ej. Ollama) orquesta la conversación y ejecuta **llamadas a herramientas** que reutilizan la misma lógica de negocio que la API REST: listado de hospitales, especialidades, consultorios, reglas de calendario/agenda, consulta de citas del paciente autenticado, creación, actualización (reagendamiento) y borrado (cancelación).

**Herramientas de dominio (referencia técnica):** `get_scheduling_rules`, `list_hospitals`, `list_specialties`, `list_consultation_rooms`, `get_appointments`, `create_appointment`, `update_appointment`, `delete_appointment` (definidas en `chat_tool_executor.py` / uso desde `openai_chat_service.py`).

**Dependencias:** usuario autenticado (JWT en cabecera, mismo mecanismo que el resto del cliente); variables `OPENAI_API_KEY` y/o `OPENAI_BASE_URL`, `OPENAI_CHAT_MODEL`, `APP_TIMEZONE`, etc., configuradas en el servicio.

**Riesgos si falla:** respuestas lentas en modelos locales; dependencia de proveedor externo; malentendidos del modelo mitigados por **validación en herramientas** y mensajes de error claros en UI.

---

### US-13 — Acceder al asistente como paciente autenticado

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **Quiero** | abrir el asistente de citas solo cuando he iniciado sesión |
| **Para** | que mis consultas y acciones se asocien a mi cuenta y no expongan datos a terceros |

**Valor de negocio:** coherencia con el modelo de seguridad del producto y trazabilidad por paciente.

**Descripción ampliada**

- La ruta del asistente debe estar **protegida** igual que el panel y la reserva clásica.
- Las peticiones `POST` al endpoint de chat incluyen el token JWT que ya usa `apiClient` / Axios.
- Sin sesión válida, el usuario no consume cuota de chat ni ve historial de citas ajeno.

**Criterios de aceptación**

1. Dado un usuario no autenticado, cuando intenta abrir el asistente, entonces es redirigido al flujo de login (o equivalente definido en la app).
2. Dado un usuario autenticado, cuando envía un mensaje al asistente, entonces la petición lleva autorización y el backend responde en el contexto de ese paciente.
3. El cierre de sesión impide seguir enviando mensajes hasta volver a autenticarse.

**Trazabilidad:** `ChatAssistant.jsx`, `chat.service.js`, `chat_controller` / router del servicio.

---

### US-14 — Conversar en lenguaje natural para consultar y gestionar citas

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **Quiero** | escribir preguntas o instrucciones en lenguaje natural |
| **Para** | consultar mis citas, iniciar una reserva o solicitar cancelación/reagendamiento sin memorizar menús técnicos |

**Valor de negocio:** reduce fricción cognitiva y tiempo para usuarios que prefieren diálogo a formularios.

**Descripción ampliada**

- El historial de la conversación se envía al backend para mantener contexto (mensajes previos usuario/asistente).
- El asistente debe poder **invocar herramientas** para: conocer reglas de fechas (“mañana”, fines de semana, primer día hábil), listar clínicas y especialidades, elegir consultorio, proponer creación o cambio de cita y listar citas existentes.
- Las operaciones que **modifican** datos (crear/actualizar/borrar cita) quedan sujetas a las mismas reglas que la API manual (slots libres, jerarquía hospital–especialidad–consultorio).

**Criterios de aceptación**

1. Dado un mensaje que implica “ver mis citas”, cuando el backend procesa la solicitud, entonces la respuesta se basa en datos reales del paciente obtenidos vía herramientas.
2. Dado un mensaje de agendamiento, cuando faltan datos obligatorios, entonces el asistente guía al usuario para completar hospital, especialidad, consultorio, fecha/hora según el flujo definido.
3. Dado un intento de acción inválida (p. ej. slot ocupado), cuando el backend rechaza la operación, entonces el usuario recibe un mensaje comprensible, no un fallo silencioso.

**Trazabilidad:** `openai_chat_service.py`, `ChatToolExecutor`, épicas C y D para reglas de negocio equivalentes.

---

### US-15 — Flujo guiado con estado de asistente y respuestas rápidas

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **Quiero** | recibir botones o pasos guiados (clínica, opciones del asistente) cuando ayuden a completar el flujo |
| **Para** | no tener que teclear todo a mano y reducir errores en pasos repetitivos |

**Valor de negocio:** combina lo mejor del chat con la precisión de selecciones estructuradas.

**Descripción ampliada**

- El backend puede devolver `wizard_state` para **continuar un flujo multi-paso**; el cliente lo reenvía en cada mensaje hasta cerrar el flujo.
- Puede devolver `quick_replies` (etiqueta + `payload` estructurado): al pulsar, el cliente envía una **selección** (`wizard_selection`) alineada con el paso actual.
- Puede devolver una lista de **hospitales** para atajos (“Elige clínica”): al pulsar, se compone un mensaje coherente con la intención previa del usuario.
- La UI debe mostrar estos controles **junto al mensaje del asistente** sin confundir selección estructurada con texto libre del usuario cuando el producto lo distingue así.

**Criterios de aceptación**

1. Dado una respuesta con `quick_replies`, cuando el usuario pulsa una opción, entonces se envía al backend el payload acordado y el hilo continúa correctamente.
2. Dado `hospitalQuickReplies`, cuando el usuario elige una clínica, entonces se construye el mensaje compuesto y se reenvía sin perder el contexto de sesión.
3. Dado un `wizard_state` activo, cuando el usuario envía nuevos mensajes, entonces el estado se mantiene hasta que el backend lo limpia o el usuario reinicia la conversación (ver US-17).

**Trazabilidad:** `ChatAssistant.jsx` (`wizardState`, `wizardSelection`, render de quick replies y hospitales), contrato de `chat.service.js`.

---

### US-16 — Límites del asistente y mensajes seguros

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **Quiero** | entender que el asistente ayuda con la **gestión de citas**, no con diagnóstico ni tratamiento |
| **Para** | no confundir orientación administrativa con consejo médico |

**Valor de negocio:** alineación con uso responsable en entorno sanitario y expectativas claras.

**Descripción ampliada**

- Los textos de la pantalla (cabecera, subtítulo, ayuda inicial) deben enfatizar **citas, agenda y cancelaciones**, no valoración clínica.
- El backend puede **sanear** texto visible (p. ej. evitar placeholders confusos en respuestas del modelo).
- Cualquier alucinación del modelo queda **acotada** por el hecho de que las acciones reales solo ocurren si las herramientas confirman datos.

**Criterios de aceptación**

1. La interfaz del asistente comunica de forma explícita su propósito (gestión de citas / lenguaje natural para agenda).
2. Las operaciones sobre la base de citas solo se reflejan si las herramientas devuelven éxito conforme a reglas de negocio.
3. El producto no presenta el asistente como sustituto del criterio del profesional de salud.

**Trazabilidad:** copy en `ChatAssistant.jsx`; `_sanitize_assistant_visible_text` y prompts en `openai_chat_service.py`.

---

### US-17 — Limpiar conversación y reiniciar el flujo

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **Quiero** | vaciar el hilo de chat y el estado del asistente cuando empiece de nuevo |
| **Para** | no arrastrar contexto equivocado en un nuevo trámite |

**Valor de negocio:** evita errores por estado obsoleto del wizard y mejora la sensación de control.

**Descripción ampliada**

- Acción “Limpiar” (o equivalente) con confirmación antes de borrar.
- Al limpiar, se resetean mensajes locales y `wizard_state` a `null`.
- El usuario puede seguir escribiendo desde cero con sugerencias iniciales si la UI las ofrece.

**Criterios de aceptación**

1. Dado un chat con mensajes y wizard activo, cuando confirmo limpiar, entonces la vista vuelve al estado inicial y el siguiente mensaje no arrastra `wizard_state` anterior.
2. La acción no puede ejecutarse accidentalmente sin confirmación si el diseño así lo establece.

**Trazabilidad:** `clearChat` en `ChatAssistant.jsx`.

---

### US-18 — Sugerencias iniciales, carga y manejo de errores del asistente

| Campo | Contenido |
|-------|-----------|
| **Como** | paciente |
| **Quiero** | ver ideas para empezar, saber cuando el sistema está procesando y recibir errores claros si algo falla |
| **Para** | no quedarme bloqueado ante timeouts, API caída o configuración incorrecta del modelo |

**Valor de negocio:** mejora la tasa de éxito del primer contacto y reduce abandono por frustración técnica.

**Descripción ampliada**

- **Sugerencias** al inicio (p. ej. ver citas, agendar mañana, cómo cancelar) que envían texto predefinido al asistente.
- Indicador de **carga** mientras el backend / modelo responde (puede tardar más en modelos locales o primer arranque de Ollama).
- **Timeout** extendido en cliente para peticiones de chat frente a respuestas lentas.
- Mensajes de error que distingan: sin conexión al backend, timeout (con pista sobre Ollama), detalle del servidor cuando la API lo devuelve.
- Toasts o burbujas de error en el hilo según el diseño actual.

**Criterios de aceptación**

1. Dado el estado vacío del chat, cuando cargo la página, entonces veo al menos tres sugerencias accionables acordes al dominio (consulta / agenda / cancelación).
2. Dado un envío de mensaje, cuando la petición está en curso, entonces veo feedback de “espera” y no puedo duplicar envíos de forma inconsistente.
3. Dado fallo de red o timeout, cuando la petición falla, entonces recibo un mensaje entendible (no solo código HTTP) y puedo reintentar.
4. Dado error de configuración del proveedor de IA en servidor, el usuario recibe orientación acorde a la política de mensajes del cliente (sin filtrar secretos).

**Trazabilidad:** `SUGGESTIONS`, `getChatErrorMessage`, timeout en `chat.service.js`, estados `sending` y mensajes `variant: 'error'` en `ChatAssistant.jsx`.

---

## 9. Criterios de éxito del producto (definición de “hecho” global)

Tomado y unificado de ambos `SPRINT_PLANNING.md`, ampliado con la Épica F:

- El paciente puede autenticarse y mantener sesión de forma coherente con el diseño.
- Puede completar una reserva respetando Hospital → Especialidad → Consultorio, calendario y slots.
- Puede ver próximas citas y el listado completo.
- Puede cancelar y reagendar con confirmación y estados alineados con la API.
- Las fechas se muestran de forma coherente respecto a zona horaria.
- La aplicación es razonablemente responsive.
- **(Épica F)** El paciente autenticado puede usar el asistente para consultar y gestionar citas en lenguaje natural, con herramientas de servidor y flujo guiado cuando aplique; errores y tiempos de espera se comunican de forma comprensible.

---

## 10. Trazabilidad rápida documento ↔ sprints / código

| Área | Documento de planificación / código |
|------|----------------------------|
| Cliente: auth, dashboard, reserva, calendario, cancelar, reagendar | `clientSide/SPRINT_PLANNING.md` |
| Servicio: slots dinámicos, hospitales, consultorios, booking, `rescheduled`, vistas SQL | `service/SPRINT_PLANNING.md` |
| Asistente IA (no en SPRINT_PLANNING legacy) | `clientSide/src/pages/ChatAssistant.jsx`, `clientSide/src/services/chat.service.js`, `service/app/services/openai_chat_service.py`, `service/app/services/chat_tool_executor.py`, controlador de `chat` en el servicio |

---

## 11. Historial de cambios

| Versión | Fecha | Cambios |
|---------|--------|---------|
| 1.0 | 2026-04-11 | Creación inicial del documento de historias de usuario y épicas ampliadas |
| 1.1 | 2026-04-11 | Épica F (asistente de IA): US-13 a US-18; visión, alcance, mapa de épicas, criterios globales y trazabilidad actualizados |

---

*Fin del documento.*
