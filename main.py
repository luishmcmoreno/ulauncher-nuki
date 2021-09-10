from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

import requests

class OpenLockerEventListener(EventListener):

    def on_event(self, event, extension):
        hed = {'Authorization': 'Bearer ' + extension.preferences['access_token'] }
        locker_id = event.get_data()['locker_id']
        open_obj = {
          'action': 3,
          'option': 0
        }
        requests.post('https://api.nuki.io/smartlock/%s/action' % (locker_id), json = open_obj, headers = hed)

class NukiExtension(Extension):

  def __init__(self):
    super(NukiExtension, self).__init__()
    self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
    self.subscribe(ItemEnterEvent, OpenLockerEventListener())
 
class KeywordQueryEventListener(EventListener):

  def on_event(self, event, extension):
    items = []
    try:

      hed = {'Authorization': 'Bearer ' + extension.preferences['access_token'] }
      req = requests.get('https://api.nuki.io/smartlock', headers = hed)
      lockers = req.json()
      if event.get_argument():
        filtered_lockers = list(filter(lambda filtered: event.get_argument().lower() in filtered['name'].lower(), lockers))
      else:
        filtered_lockers = lockers
      if (len(filtered_lockers) > 0):
        for locker in filtered_lockers:
          items.append(ExtensionResultItem(icon='images/icon.png',
            name='%s' % ( locker['name'] ),
            description='Press \'enter\' to  open %s' % (locker['name']),
            on_enter=ExtensionCustomAction({'locker_id': locker['smartlockId']})
          ))
      else:
        items.append(ExtensionResultItem(icon='images/icon.png',
          name = event.get_argument(),
          description = 'No lockers found containing \'%s\'' % (event.get_argument()),
          on_enter= HideWindowAction()
        ))

    except NameError as errorMessage:
      items.append(ExtensionResultItem(icon='images/icon.png',
        name='Expr: %s' % errorMessage,
        description='Expression has Error.'
      ))

    return RenderResultListAction(items)


if __name__ == '__main__':
   NukiExtension().run()
