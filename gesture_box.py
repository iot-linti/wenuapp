#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kivy.gesture import GestureDatabase
from kivy.uix.boxlayout import BoxLayout
from kivy.gesture import Gesture

gesture_strings = {
    'top': 'eNqlmE1yHDcMhfd9EWsTFfFPXkDepsoHSMn2lKyyI01JchLfPiAb0y1InWw4m5EwJMD3PTTJmav77/d//bq+Oz2//Hw6LR/j/VyWq69nWD59eLj98/RhOaP/6W+0PH/68Pzy9Pj99Oz/8nL14yzL1WGST2PYctaeynz++fH+4aVPq31a+49pv/dRyxnWFfQl/PIpgMtNuWbD1hQrS4GiINaX80//mPrHpRQiMC7NVNnUlH3Bn2//vxCPQrLcRQ0G4AZSjKm01mvczaQf8sG29KVRwQLaqgDVyeR1JG+X5GRQqrB4ApFKbS47DgsQtuyeuJhxY23o2OaS40hOW3Ig0+EpAAryJHYcruLmKjoQ5iKyoieaTD9cxc1VlFJUiSs0Iayz4IetuNmKUBE6ciYjtcmmoWErbbZC9TSoQg2tguefTD+Mpc1Y8H7ES8/wbMfT8JU2XwFRrS8bBn3SyfTDV9p89clYYq/xvpx9omgYS5uxxakLeg1qfcepk13Jw1nenC1oTsT3s1qbtFljeRjLm7HORaVa4VoJ0XDSWR7Ocjj7m2eh4gtnrNXYyLf+yfzDWrY9v1Yu3GqjUaTKZP7hLbc9vyeuqE2plQ5qcv0yzBXY8vs26cdhdUpcFdps88iwV2jP7wvnWLwnm9zvZdgru71QG2PkEN8XZvEMe2W3FxG8/ZGA0XdnbrN4hr2y2+s7ZnUDoGolFT8lp9LrcFd3d30v9ke2XApMPlw6zNXdXHIwFYs0Zus9NLlv6nBXd3fJqTdP1Mw3IS00+XDpcFd3d8nYLwx9XxiMJvdlHebqbi574wi/Wv9cfhvu2u6uX2DFdvowuTXbsNd2e/209XtCvQDiSfw27LXdXr8d+5HCfnj5dVnh0j191ytOy9QfjX5R5FagZ+/fGr48nU4P23cA0/4lwGy5uvFWuS7LDVefvbyc/X5zuwetrcGWgnUEa0lBXYOQgrIGMQVpDVIK4hrkFFyX5GfDq6C2TnF/aR+haYSt0ywF5bq9fnEfkbQqr9OSVqX31VoSLu194pYoyMqrJQqyLrIlCrLyaomC0EGBhERWeC1REFiDiQKvfrYknO2gQKLA+p4ClISB16VDSdKZIpq0M0Y0iedyVCShoBYTk3zS9+v3S+ObIevERIP4qGJiQxcBiQeVg4pQ3gwZEyHxwBrRxAMtookH8lERfjNknZh4YOCFhAAhogkB1KMi9c2QdWJCAEEUk2qILsCkGgIiJtUQhDCpLmExJqElCGESWo7aEpPqEoQwqS6XBSWhJQhhElqO2pJeq6YWhAhSNNZMmKJBiChFjzqROA0JV0lS9KgT6TUCqkGULEXrUcWahoTF1FL0qC058aiBlxOPGgI48YhjBzjxsKO25MTD7EAAJzhxJgEnHhYtwYmHH0AHFeubIevExMPgYB2SeMQ5BpJ4xDEFknjEKQSSeCgcrE4SjzhlQBKCOFFAEgIJgyQhiGMEJKnmdlS6vRkyJmpSzaFPk2oOTzSpvpwTmlRzPJCahFII1SSUQqgmoRQ0NQmlEKohFNZouKTtdRRDm5UUDRUGKSoHrWCYhoRQvy3erjezb6f7u28v/VdUv+fdwLgXePjv+68v30ZUPLrGXh5/nJ5uH76cRlzHLzA9HtfGP85Pj19/fllz2XKD1wb9HurdWMyfHr9cPX++/hcOCHKG',
    'down': 'eNqlWNtuG0cMfd8fiV9iDO/DH3BfC+QDCicRHCOpLdhK2/x9uSNqJcrbBsj6RfEx5wx5Doczys3j18e/ftw+7F4P319202/5uW/Tzec9TB/ePd3/uXs37TH+GR80vX5493p4ef66e41febr5tpfpZpXkwwib9jpTWazfPz8+HeZlfV7m/7Hs9zlq2sMxgzmFH7EEcLp7324FCNUaU3fqSjqn88/8Z5ru2m1rpg6NPP7I6hTo68f7/9+GxzYyPeQOrEKKXRDNmqsFxcOvs4/awc7sbOTdemNsvTnaJvY+2P3M3oQ7KqCJAvXOW9hxGICwsFM3gS7cunsX2EaOg5zO5ALiQWHQDU15kzA4TMWzqYSg0sJRju5xM0n29zM9h9uxiasYouLP2YepeDY11sdKIDJgDIpN5MNTPHsadkYjNjJv0sl5CzkNS+lsKRJ0dIcOHF3fFtV/jX14SmdPwcPSyJ6Z0LrIJmFoeEpnT6Nf3EipGTaEpps8peEpnT2FkANBiB1Com26DEvpbGkk20JxiJYHigPbt7Dz8JTPnjZrkTdGL8aBNRLfxD485bOnjaLFJSaMRWN630Y+LOWzpQ3ijFIjcLAOwrZNmeEpp6czu2vcHTF9YwooOWwiH6ayL+Qi4hLnKT4xRi9uIZfhqcBC7hCkZBLTqwMtd9KvkQ9LhU7kgMAafR7zMWYBsl5MXrBG0U0eV210kvafj14Znoos7CzR6DEHOoX4ohvZh6WyWBqDizgWxyaO0sS2sQ9PZfEUm6DH0G0kpkQim9h1mKqLqciAGBcex4GNx8BG3XW4qourcf5BucWdSU27bSQfpupiaszceLtgNGRMdkXhbezDVF1MjUZvhKF5CG8M2zzV4akunkYXuiHHlaoxyGIYbGK34aktnpLHUwXFtcc5ct+mug1LbbE0plY8Sy1eMvH6sq2e2vDUFk9Z4mWEcUrjMMUo8Z+Rz98DPr3sdk/Lqz4Sime92XRzR0K3bbqLFrn1yx+bDvsY6vcXERobXPzQHOFXEW84eisR/pajw2UE4UoEXkW83YVKhKxwcImIWmZQCmgrxFoi/LjMLkHGI1jE4hU5exGLZSzzog+vKOhFH+7HZUUS9pVlRRKB47JUAY/gitaeksAxgo/LtICyspuVCDsu6wU8iud+CWobILRWUEwUCiqJYkE1USpoT5QL6omWIg0SLVXaKYdSmXGipTQ7ZVZqs6MKAKU2y8yg1NZTByi19cwMSm2dEi21da5m6ggphfaUCkqh3dYWlqp76gb9Ci19wCOkSOApIhYJPAvAIoFndlgk8JQLiwSeCeGlBDH5EpWC4kp9qCWEVipBKyFpMfaCpsXoBc2cqRV0TS66lIAgCyAsKK0UQFRCsi2p6AGytmMRB7IAKnqAr+1Y9MBsWCp6YPpNRQ9Mv7nogbKyCRc9MFuCix6Y8jJdDDOiTIi5oLC2iZSQzJm1oKkoW0GzC7gXNEVkL2imKe0S5UxToKBpvGBBUzehK/Stq1Kq5tRNSqGcaUopdL5Q3igkpWrO0yb9Cl3Jo0ggKa0WCSTL0iKBpLSKV+jbTbToIamzFglkrYW16KEpuuoVurJj0UOzN7TocbqItEigKboVCU7XkxUJLHvDigS21sJWJDBcydmKHqeLy4oEljlbkcDWbgQrEsQttrJj0eN0pVnR43Sl9aLH6UrrRY+40t5u0os4pyutFz36Wk/3osfpSutFD29rO4Y4x2f0l93jw5fD/J/Y8QS8i8a5fghFzN+Pnw9fRkiPiypYAzs8f9u93D992g3cx/fhGc/3/h/7l+fP3z8NYp+vt1u10Nu7aDwXeP6u/PH2X67DxfE=',
}

#This database can compare gestures the user makes to its stored     gestures
#and tell us if the user input matches any of them.
gestures = GestureDatabase()
for name, gesture_string in gesture_strings.items():
    gesture = gestures.str_to_gesture(gesture_string)
    gesture.name = name
    gestures.add_gesture(gesture)

class GestureBox(BoxLayout):

    def __init__(self, **kwargs):
        for name in gesture_strings:
            self.register_event_type('on_{}'.format(name))
        super(GestureBox, self).__init__(**kwargs)

    def on_left_to_right_line(self):
        pass

#To recognize a gesture, you’ll need to start recording each individual event in the
#touch_down handler, add the data points for each call to touch_move , and then do the
#gesture calculations when all data points have been received in the touch_up handler.


    def on_touch_down(self, touch):
        #create an user defined variable and add the touch coordinates
        touch.ud['gesture_path'] = [(touch.x, touch.y)]
        super(GestureBox, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        touch.ud['gesture_path'].append((touch.x, touch.y))
        super(GestureBox, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if 'gesture_path' in touch.ud:
            #create a gesture object
            gesture = Gesture()
            #add the movement coordinates
            gesture.add_stroke(touch.ud['gesture_path'])
            #normalize so thwu willtolerate size variations
            gesture.normalize()
            #minscore to be attained for a match to be true
            match = gestures.find(gesture, minscore=0.3)
            if match:
                print("{} happened".format(match[1].name))
                self.dispatch('on_{}'.format(match[1].name))
        super(GestureBox, self).on_touch_up(touch)

