from collections import deque
import random

class Card:

  suits = {
    1: '♥',
    2: '♦',
    3: '♣',
    4: '♠'
  }
  ranks = {
    1: 'A',
    11: 'J',
    12: 'Q',
    13: 'K'
  }
  for i in range(2, 11):
    ranks[i] = str(i)

  def __init__(self, rank, suit):
    self.rank = rank
    self.suit = suit
  
  def __repr__(self):
    return Card.ranks[self.rank] + Card.suits[self.suit]

class Deck:
  def __init__(self):
    self.cards = deque([Card(rank, suit) for rank in Card.ranks.keys() for suit in Card.suits.keys()])
    self.shuffle()

  def shuffle(self):
    random.shuffle(self.cards)

  def draw(self, num=1):
    if num == 1:
      return self.cards.pop()
    else:
      return [self.cards.pop() for _ in range(num)]
