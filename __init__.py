import json
from typing import Any, Dict, List, Optional

import requests
from anki import Collection
from anki.notes import Note
from anki.decks import Deck
from anki.models import NoteType
from aqt import mw
from aqt.qt import *
from aqt.utils import qconnect, showInfo

widgetsDeckName='Flutter Widgets'
widgetModelName='Flutter Widget'
widgetsCatalogUrl='https://raw.githubusercontent.com/flutter/website/master/src/_data/catalog/widgets.json'

Widget = Dict[str, Any]

def widgetsDeckExists(col: Collection) -> bool:
    return col.decks.byName(widgetsDeckName) is not None

def setupWidgetsDeck(col: Collection) -> Deck:
    deckId = col.decks.id(widgetsDeckName)
    return col.decks.get(deckId)

def setupWidgetModel(col: Collection) -> NoteType:
    models = col.models
    model = models.byName(widgetModelName)

    if model is None:
        model = models.new(widgetModelName)
        # Fields
        models.add_field(model, models.new_field("Name"))
        models.add_field(model, models.new_field("Description"))
        models.add_field(model, models.new_field("URL"))

        # Config
        model['css'] = '''
.card {
    font-family: arial;
    font-size: 20px;
    color: black;
    background-color: white;
}
'''

        # Cards
        template = models.new_template("Card 1")
        template['qfmt'] = '''
<p>{{Name}}</p>
'''
        template['afmt'] = '''
{{FrontSide}}

<hr/>

<p>{{Description}}</p>

<p><a href="{{URL}}">Docs</a></p>
'''
        models.add_template(model, template)

        models.save(model)

    return model

def downloadWidgetsCatalog() -> List[Widget]:
    response = requests.get(widgetsCatalogUrl)
    if (response.status_code != 200):
        raise Exception(f"Could not download Flutter widgets catalog: {response.status_code}: {response.content}")
    return json.loads(response.content)

def createWidgetNotes(col: Collection, deck: Any, model: Any, catalog: List[Widget]) -> None:
    for widget in catalog:
        note = Note(col, model)
        note['Name'] = widget['name']
        note['Description'] = widget['description']
        note['URL'] = widget['link']
        col.add_note(note, deck['id'])

def importWidgets(col: Collection) -> Optional[Deck]:
    # Abort import if deck already exists.
    if widgetsDeckExists(col):
        return

    deck = setupWidgetsDeck(col)
    model = setupWidgetModel(col)
    catalog = downloadWidgetsCatalog()
    createWidgetNotes(col, deck, model, catalog)

    return deck

def importWidgetsActionFn() -> None:
    deck = importWidgets(mw.col)
    if deck is None:
        return

    mw.reset()

importWidgetsAction = QAction('Import Flutter Widgets', mw)
qconnect(importWidgetsAction.triggered, importWidgetsActionFn)
mw.form.menuTools.addAction(importWidgetsAction)
