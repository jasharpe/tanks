import pygame
import constants
from game_event import NewGameEvent, QuitEvent

class MenuItem:
  def __init__(self, text, on_activate):
    self.raw_text = text
    self.activate = on_activate
    self.selected = False
    self.generate_image()

  def generate_image(self):
    color = (200, 200, 200)
    if self.selected:
      color = (255, 200, 200)
    self.text = pygame.font.Font(None, 36).render(self.raw_text, 1, color)

  def toggle_selected(self):
    self.selected = not self.selected
    self.generate_image()

def new_game_menu_action(game):
  game.register_event(NewGameEvent())

def quit_menu_action(game):
  game.register_event(QuitEvent())

class Menu:
  def __init__(self, game):
    self.game = game
    self.menu_items = [
        MenuItem("New Game", new_game_menu_action),
        MenuItem("Quit", quit_menu_action)
    ]
    self.menu_items[0].toggle_selected()
    self.selected = 0

  def update(self, delta, events, pressed, mouse):
    for event in events:
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_DOWN:
          self.menu_items[self.selected].toggle_selected()
          self.selected = (self.selected + 1) % len(self.menu_items)
          self.menu_items[self.selected].toggle_selected()
        elif event.key == pygame.K_UP:
          self.menu_items[self.selected].toggle_selected()
          self.selected = (self.selected - 1) % len(self.menu_items)
          self.menu_items[self.selected].toggle_selected()
        elif event.key == pygame.K_RETURN:
          self.menu_items[self.selected].activate(self.game)

  def draw(self, screen):
    text_top = 300
    for menu_item in self.menu_items:
      text_pos = menu_item.text.get_rect(centerx = constants.RESOLUTION_X / 2)
      text_pos.top = text_top
      text_top += menu_item.text.get_height()
      screen.blit(menu_item.text, text_pos)
