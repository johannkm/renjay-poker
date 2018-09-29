from model import Model, SelectionItem, Card, Deck, Hand, HandScoring
from view import View

import readchar
import sys
import time

RANKS = 13
SUITS = 4

def main():
  Controller().run_game()

class Controller:
  def __init__(self):
    self.model = Model()
    self.view = View()

    top_row = [SelectionItem('', is_top_left=True)] + [
      SelectionItem(Card.ranks[rank], is_card=False, is_top_row=True) for rank in range(1, RANKS + 1)
    ]
    self.model.selection_matrix = [top_row] + [
      [SelectionItem(str(Card(rank, suit)), card=Card(rank, suit)) for rank in range(1,RANKS + 1)] for suit in range(1,SUITS + 1)
    ]
    for i in range(1, len(self.model.selection_matrix)):
      self.model.selection_matrix[i] = [SelectionItem(Card.suits[i], is_card=False)] + self.model.selection_matrix[i]

    for row in self.model.selection_matrix:
      for item in row:
        item.is_selected = False

    self.model.deck = Deck()
    self.model.player_hand = Hand()
    self.model.dealer_hand = Hand()
    self.model.drawn_cards = []

  def run_game(self):
    while True:
      self.get_selection()
      self.model.state = self.model.GameMode.DRAWING
      self.render()

      done = False
      self.model.drawn_cards = []
      self.model.cursor=[0,0]
      while not done:
        card = self.model.deck.draw()
        self.model.drawn_cards.append(card)

        if card in self.model.filter:
          self.model.player_hand.add_card(card)
          done = True
        else:
          self.model.dealer_hand.add_card(card)

        self.render()

        if len(self.model.deck.cards) == 0:
          done = True

        time.sleep(0.8)

      if self.model.player_hand.size() >= 5:
        if self.model.dealer_hand.size() < 8:
          self.model.state = self.model.GameMode.FINISHING
          while self.model.dealer_hand.size() < 8:
            card = self.model.deck.draw()
            self.model.drawn_cards.append(card)
            self.model.dealer_hand.add_card(card)
            self.render()
            time.sleep(0.8)

        won = HandScoring.compare_hands(self.model.player_hand.hand, self.model.dealer_hand.hand) == 1
        self.model.message = 'YOU WIN' if won else 'YOU LOSE'
        self.render()
        sys.exit(0)

      if len(self.model.deck.cards) == 0:
        # player lose, dealer got entire rest of the deck
        self.model.message = 'YOU LOSE'
        self.render()
        sys.exit(0)


  def render(self):
    self.view.render(self.model)

  def get_selection(self):
    for row in self.model.selection_matrix[1:]:
      for item in row[1:]:
        if not self.model.card_available(item.card):
          item.is_selected = False

    self.model.cursor = [1,1]
    self.model.state = self.model.GameMode.FILTERING
    model = self.model
    self.render()

    while True:
      keypress = readchar.readkey()
      if keypress == readchar.key.UP:
        if model.cursor[0] > 1 or model.cursor[0] == 1 and model.cursor[1] > 0:
          model.cursor[0] -= 1
          self.render()
      elif keypress == readchar.key.DOWN:
        if model.cursor[0] < len(model.selection_matrix) - 1:
          model.cursor[0] += 1
          self.render()
      elif keypress == readchar.key.LEFT:
        if model.cursor[1] > 1 or model.cursor[1] == 1 and model.cursor[0] > 0:
          model.cursor[1] -= 1
          self.render()
      elif keypress == readchar.key.RIGHT:
        if model.cursor[1] < len(model.selection_matrix[0]) - 1:
          model.cursor[1] += 1
          self.render()

      elif keypress == readchar.key.SPACE:
        self.make_selection(model.cursor)
        self.render()
      elif keypress == readchar.key.ENTER:
        selected_cards = set()
        for row in model.selection_matrix[1:]:
          for card_item in row[1:]:
            if card_item.is_selected:
              selected_cards.add(card_item.card)
        if len(selected_cards) > 0:
          model.filter = selected_cards
          break

      elif keypress in (readchar.key.CR, readchar.key.CTRL_C):
          sys.exit(1)
  
  def make_selection(self, cursor):
    i, j = cursor[0], cursor[1]
    if i > 0 and j > 0:
      card = self.model.selection_matrix[i][j].card
      if not (card in self.model.player_hand.hand or card in self.model.dealer_hand.hand):
        self.model.selection_matrix[i][j].is_selected = not self.model.selection_matrix[i][j].is_selected
    elif i == 0:
      any_false = False
      for i_ in range(1, SUITS + 1):
        if not self.model.selection_matrix[i_][j].is_selected and self.model.card_available(self.model.selection_matrix[i_][j].card):
          any_false = True
          break
      for i_ in range(1, SUITS + 1):
        if self.model.card_available(self.model.selection_matrix[i_][j].card):
          self.model.selection_matrix[i_][j].is_selected = any_false
    elif j == 0:
      any_false = False
      for j_ in range(1, RANKS + 1):
        if not self.model.selection_matrix[i][j_].is_selected and self.model.card_available(self.model.selection_matrix[i][j_].card):
          any_false = True
          break
      for j_ in range(1, RANKS + 1):
        if self.model.card_available(self.model.selection_matrix[i][j_].card):
          self.model.selection_matrix[i][j_].is_selected = any_false
    
    


if __name__ == '__main__':
  main()