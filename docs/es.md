# slopcheck

Un skill de Claude Code que audita la prosa contra los hábitos que la hacen sonar a
máquina, y ayuda a reescribirla.

Español · English · Português · Français. Agregar un idioma es un archivo JSON, no un
cambio de código.

## Por qué

Los modelos de lenguaje escriben en un dialecto reconocible. Antítesis cada tres líneas,
listas de tres, un cierre simétrico con moño, y oraciones que caen todas al mismo largo.
Nada de eso está mal. Todo es reconocible, y el lector que lo nota a medias deja de
confiar en la página.

El costo no es estético. Un documento servía como prueba de que alguien pensó: el hueco
de tu propio argumento aparecía justo en el párrafo donde tenías que explicarlo. Cuando
el borrador llega ya formado, ese momento se puede saltar y desde el archivo terminado
nadie lo distingue.

slopcheck no devuelve el pensamiento. Hace visible el salto.

## Instalación

**Como plugin de Claude Code**

```
/plugin marketplace add zamarrong/slopcheck
/plugin install slopcheck
```

**Como skill personal**

```bash
git clone https://github.com/zamarrong/slopcheck.git
cp -r slopcheck/skills/slopcheck ~/.claude/skills/
```

**Como herramienta de línea de comandos** — sin Claude, sin dependencias, Python 3.8+

```bash
python3 skills/slopcheck/scripts/slopcheck.py borrador.md
cat borrador.md | python3 skills/slopcheck/scripts/slopcheck.py --lang es
```

## Qué revisa

Antítesis · triadas · metalenguaje · léxico inflado · gerundios apilados · atribución
vaga · aperturas y cierres de molde · rayas, flechas y negritas · variación del largo de
oración · tasa de cópula.

Cada hallazgo trae un presupuesto, por qué importa y cómo se arregla. Algunos patrones
se permiten una vez. Una antítesis puede ser la mejor línea del párrafo; siete son una
firma.

## Los fixtures son reales

`tests/fixtures/slop_es.txt` es un primer borrador auténtico, escrito por un modelo, que
su autor rechazó con "tu redacción es muy IA Style". `human_es.txt` es la versión que se
publicó después de reescribirlo. La suite de pruebas exige que la herramienta los
distinga: cinco hallazgos contra cero.

Esa es la vara. Una herramienta que marca todo sirve tan poco como una que no marca nada.

## Qué no es

**No es un detector de IA.** No puede decirte quién ni qué escribió un texto. Marca
construcciones, y los escritores humanos cuidadosos usan todas. No lo uses para acusar a
un estudiante, a un colega ni a un candidato. No existe un umbral a partir del cual se
vuelva evidencia.

**No sirve para ocultar uso de IA no declarado.** Si una revista, un profesor, un cliente
o un lector merecen una declaración, limpiar la prosa no la sustituye. En
`skills/slopcheck/references/disclosure.md` están las reglas de ICMJE, COPE y el AI Act
europeo.

**No es una guía de estilo.** Tiene opiniones sobre hábitos de máquina, no sobre comas.

## Contribuir

Los paquetes de idioma son la contribución más valiosa y la más fácil de revisar. El
motor no tiene nada específico del inglés: un idioma es un archivo de datos con patrones,
etiquetas y textos de interfaz. Ver [CONTRIBUTING.md](../CONTRIBUTING.md).

Se buscan: alemán, italiano, neerlandés, polaco, japonés, coreano, hindi, árabe, turco,
indonesio.

## Licencia

MIT.
