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
  '''
  Manage progress through game
  '''

  def __init__(self):
    self.model = Model()
    self.view = View()

    # create selection matrix for filter

    # create top row of card ranks
    top_row = [SelectionItem('', is_top_left=True)] + [
      SelectionItem(Card.ranks[rank], is_card=False, is_top_row=True) for rank in range(1, RANKS + 1)
    ]

    # create selection item for each card
    self.model.selection_matrix = [top_row] + [
      [SelectionItem(str(Card(rank, suit)), card=Card(rank, suit)) for rank in range(1,RANKS + 1)] for suit in range(1,SUITS + 1)
    ]

    # add leftmost column for suits
    for i in range(1, len(self.model.selection_matrix)):
      self.model.selection_matrix[i] = [SelectionItem(Card.suits[i], is_card=False)] + self.model.selection_matrix[i]

    # deselect all
    for row in self.model.selection_matrix:
      for item in row:
        item.is_selected = False

    # initialize game state
    self.model.deck = Deck()
    self.model.player_hand = Hand()
    self.model.dealer_hand = Hand()
    self.model.drawn_cards = []

  def run_game(self):
    '''
    Alternate between choosing filter and drawing cards until game ends
    '''

    while True:
      # get card filter
      self.get_selection()

      # start drawing
      self.model.state = self.model.GameMode.DRAWING
      self.render()

      done = False
      self.model.drawn_cards = []
      self.model.cursor=[0,0] # move cursor off board
      while not done:

        # draw card
        card = self.model.deck.draw()
        self.model.drawn_cards.append(card)

        # give it to player or dealer
        if card in self.model.filter:
          self.model.player_hand.add_card(card)
          done = True # player got card, stop drawing
        else:
          self.model.dealer_hand.add_card(card)

        # update view
        self.render()

        # if out of cards
        if len(self.model.deck.cards) == 0:
          done = True

        # delay until next draw
        time.sleep(0.8)

      # check if game over
      if self.model.player_hand.size() >= 5:

        # draw until dealer has at least 8 cards
        if self.model.dealer_hand.size() < 8:
          self.model.state = self.model.GameMode.FINISHING
          while self.model.dealer_hand.size() < 8:
            card = self.model.deck.draw()
            self.model.drawn_cards.append(card)
            self.model.dealer_hand.add_card(card)
            self.render()
            time.sleep(0.8)

        # check winner
        won = HandScoring.compare_hands(self.model.player_hand.hand, self.model.dealer_hand.hand) == 1
        self.model.message = 'YOU WIN' if won else 'YOU LOSE'
        self.render()
        sys.exit(0)

      # alternate end condition: player got less than 5 cards from entire deck
      if len(self.model.deck.cards) == 0:

        # player loses by default
        self.model.message = 'YOU LOSE'
        self.render()
        sys.exit(0)


  def render(self):
    '''
    Update the view with the new model
    '''
    self.view.render(self.model)

  def get_selection(self):
    '''
    Get the selection of filtered cards from the user
    '''

    # deselect all drawn cards
    for row in self.model.selection_matrix[1:]:
      for item in row[1:]:
        if not self.model.card_available(item.card):
          item.is_selected = False

    # reset selection box
    self.model.cursor = [1,1]
    self.model.state = self.model.GameMode.FILTERING
    model = self.model
    self.render()

    # move cursor and handle item selection
    while True:
      keypress = readchar.readkey()

      # if not at edge, move cursor in specified direction
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

      # handle selection
      elif keypress == readchar.key.SPACE:
        self.make_selection(model.cursor)
        self.render()

      # if at least one card is selected, stop selection
      elif keypress == readchar.key.ENTER:
        selected_cards = set()
        for row in model.selection_matrix[1:]:
          for card_item in row[1:]:
            if card_item.is_selected:
              selected_cards.add(card_item.card)
        if len(selected_cards) > 0:
          model.filter = selected_cards
          break

      # escape sequences
      elif keypress in (readchar.key.CR, readchar.key.CTRL_C):
          sys.exit(1)
  
  def make_selection(self, cursor):
    '''
    Handle a selection of either an individual card or an entire suit or rank
    '''
    i, j = cursor[0], cursor[1]

    # individual card selected
    if i > 0 and j > 0:
      card = self.model.selection_matrix[i][j].card

      # if card has not been drawn
      if self.model.card_available(card):
        self.model.selection_matrix[i][j].is_selected = not self.model.selection_matrix[i][j].is_selected

    # rank selected
    elif i == 0:

      # check if any of this column are not selected
      any_false = False
      for i_ in range(1, SUITS + 1):
        if not self.model.selection_matrix[i_][j].is_selected and self.model.card_available(self.model.selection_matrix[i_][j].card):
          any_false = True
          break

      # set all to true if some were not, otherwise all to false
      for i_ in range(1, SUITS + 1):
        if self.model.card_available(self.model.selection_matrix[i_][j].card):
          self.model.selection_matrix[i_][j].is_selected = any_false

    # suit selected
    elif j == 0:

      # check if any of this row are not selected
      any_false = False
      for j_ in range(1, RANKS + 1):
        if not self.model.selection_matrix[i][j_].is_selected and self.model.card_available(self.model.selection_matrix[i][j_].card):
          any_false = True
          break
      
      # set all to true if some were not, otherwise all to false
      for j_ in range(1, RANKS + 1):
        if self.model.card_available(self.model.selection_matrix[i][j_].card):
          self.model.selection_matrix[i][j_].is_selected = any_false
    
    
if __name__ == '__main__':
  main()