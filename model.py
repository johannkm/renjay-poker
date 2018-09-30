from collections import deque, Counter
import random
from enum import Enum
from functools import total_ordering


class Model:
  '''
  Hold game state
  '''
  class GameMode(Enum):
    FILTERING = 1
    DRAWING = 2
    FINISHING = 3

  def __init__(self):
    self.selection_matrix = None # box of selectable items
    self.cursor = None # cursor position
    self.state = None # current game mode
    self.deck = None # Deck() object
    self.player_hand = None # set object
    self.dealer_hand = None # set object
    self.filter = None # set of selected cards
    self.drawn_cards = None # list of cards from current draw phase
    self.message = None # game over message
    self.hand_ranks = HandScoring.HandRanks # poker hands

  def card_available(self, card):
    '''
    Card can be selected for filter (has not been drawn yet)
    '''
    return not (card in self.player_hand.hand or card in self.dealer_hand.hand)


class SelectionItem:
  '''
  Item for filter selection box
  '''
  def __init__(self, value, is_selected=False, card=None, is_card=True, is_top_row = False, is_top_left=False):
    self.value = value
    self.card = card
    self.is_selected = is_selected
    self.is_card = is_card
    self.is_top_row = is_top_row
    self.is_top_left = is_top_left

class Hand:
  '''
  Set of any number of cards
  '''
  def __init__(self):
    self.hand = set()

  def add_card(self, card):
    self.hand.add(card)

  def size(self):
    return len(self.hand)

  def get_hand(self):
    return sorted(list(self.hand))

  def score(self):
    return HandScoring.score(self.hand)

class HandScoring:
  '''
  Poker hand evaluation
  '''
  class HandRanks(Enum):
    STRAIGHT_FLUSH = 1
    FOUR_KIND = 2
    FULL_HOUSE = 3
    FLUSH = 4
    STRAIGHT = 5
    THREE_KIND = 6
    TWO_PAIR = 7
    ONE_PAIR = 8
    HIGH_CARD = 9
    
  def score(hand):
    '''
    Return the name and set of relevant cards for the best poker hand.
    Suits are ignored for choosing highest ranked hand, because they
    are ignored in ties in Renj poker.
    '''
    if len(hand) == 0:
      return None

    hands = HandScoring.HandRanks

    def get_counts(hand):
      '''
      Get number of each rank and suit in the hand
      '''
      rank_counts = Counter([card.rank for card in hand])
      suit_counts = Counter([card.suit for card in hand])
      return rank_counts, suit_counts    

    '''
    Each of these detects the specified hand in some subset of the cards
    '''

    def four_kind(hand):
      rank_counts, _ = get_counts(hand)
      ranks = sorted([rank for rank, count in rank_counts.most_common() if count == 4])
      if len(ranks) > 0:
        # choose best available 4 of kind by rank
        cards = set([card for card in hand if card.rank == ranks[-1]])
        return (hands.FOUR_KIND, cards)
      return (hands.FOUR_KIND, None)

    def fullhouse(hand):
      rank_counts, _ = get_counts(hand)
      ranks_3 = sorted([rank for rank, count in rank_counts.most_common() if count == 3])
      ranks_2 = sorted([rank for rank, count in rank_counts.most_common() if count == 2 or count == 3])

      if len(ranks_3) > 0:
        # choose best rank for 3-of-kind
        best_rank_3 = ranks_3[-1]
        ranks_2.remove(best_rank_3)

        # choose best remaining rank for pair
        if len(ranks_2) > 0:
          best_rank_2 = ranks_2[-1]
          cards = set([card for card in hand if card.rank == best_rank_3])
          for card in hand:
            if card.rank == best_rank_2:
              cards.add(card)
              if len(cards) == 5:
                break
          return (hands.FULL_HOUSE, cards)

      return (hands.FULL_HOUSE, None)

    def flush(hand):
      _, suit_counts = get_counts(hand)
      suits = [suit for suit, count in suit_counts.most_common() if count >= 5]
      if len(suits) > 0:
        all_flush_cards = sorted([card for card in hand if card.suit in suits])

        # choose best ranked flush
        top_ranked_suit = all_flush_cards[-1].suit
        cards = sorted([card for card in all_flush_cards if card.suit == top_ranked_suit], reverse=True)[:5]
        return (hands.FLUSH, set(cards))
      return (hands.FLUSH, None)

    def straight(hand):
      rank_counts, _ = get_counts(hand)
      i = 13

      # starting from highest ranks, look for straight
      while i >= 5:
        no_gaps = True
        for j in range(i, i - 5, -1):
          if rank_counts[j] == 0:
            no_gaps = False
            i = j - 1
            break
        if no_gaps:
          cards = set()
          for k in range(i - 4, i + 1):
            cards.add([card for card in hand if card.rank == k][0])
          return (hands.STRAIGHT, cards)
      return (hands.STRAIGHT, None)
    
    def three_kind(hand):
      rank_counts, _ = get_counts(hand)
      ranks = sorted([rank for rank, count in rank_counts.most_common() if count == 3])
      if len(ranks) > 0:
        cards = set([card for card in hand if card.rank == ranks[-1]])
        return (hands.THREE_KIND, cards)
      return (hands.THREE_KIND, None)

    def two_pair(hand):
      rank_counts, _ = get_counts(hand)
      ranks = sorted([rank for rank, count in rank_counts.most_common() if count == 2])
      if len(ranks) >= 2:
        cards = set([card for card in hand if card.rank == ranks[-1] or card.rank == ranks[-2]])
        return (hands.TWO_PAIR, cards)
      return (hands.TWO_PAIR, None)

    def pair(hand):
      rank_counts, _ = get_counts(hand)
      ranks = sorted([rank for rank, count in rank_counts.most_common() if count == 2])
      if len(ranks) == 1:
        cards = set([card for card in hand if card.rank == ranks[-1]])
        return (hands.ONE_PAIR, cards)
      return (hands.ONE_PAIR, None)

    def high_card(hand):
      rank_counts, _ = get_counts(hand)
      ranks = sorted([rank for rank, count in rank_counts.most_common() if count == 1])
      if len(ranks) > 0:
        cards = set([card for card in hand if card.rank == ranks[-1]])
        return (hands.HIGH_CARD, cards)
      return (hands.HIGH_CARD, None)

    def straight_flush(hand):
      _, suit_counts = get_counts(hand)
      suits = [suit for suit, count in suit_counts.most_common() if count >= 5]

      straights = []
      for suit in suits:
        _, cards = straight(set([card for card in hand if card.suit == suit]))
        if cards != None:
          straights.append(cards)

      # off all available straights, choose highest
      if len(straights) > 0:
        best_straight = straights[0]
        for curr_straight in straights[1:]:
          if HandScoring.compare_hands(curr_straight, best_straight):
            best_straight = curr_straight
        return (hands.STRAIGHT_FLUSH, best_straight)
      return (hands.STRAIGHT_FLUSH, None)

    hand_test_funcs = [
      straight_flush,
      four_kind,
      fullhouse,
      flush,
      straight,
      three_kind,
      two_pair,
      pair,
      high_card
    ]

    for func in hand_test_funcs:
      hand_rank, cards = func(hand)
      if cards != None:
        return (hand_rank, cards)
    return None
  
  def compare_hands(hand1, hand2):
    '''
    Return which hand beats the other
    '''

    hand_rank1, cards1 = HandScoring.score(hand1)
    hand_rank2, cards2 = HandScoring.score(hand2)

    if hand_rank1.value > hand_rank2.value:
      return -1
    elif hand_rank1.value < hand_rank2.value:
      return 1
    else:

      # both have the same hand, compare by ranks
      if hand_rank1 == HandScoring.HandRanks.FULL_HOUSE:
        # rank of 3 pair is most significant
        rank_counts_1 = Counter([card.rank for card in cards1])
        rank_counts_2 = Counter([card.rank for card in cards2])

        if rank_counts_1.most_common(1)[0].rank < rank_counts_2.most_common(1)[0].rank:
          return -1
        elif rank_counts_1.most_common(1)[0].rank > rank_counts_2.most_common(1)[0].rank:
          return 1
        else:
          raise 'More than 4 of 1 rank in deck'

      # compare top cards by rank, continue down until mismatch is found
      else:
        for card1, card2 in zip(sorted(cards1, reverse=True), sorted(cards2, reverse=True)):
          if card1.rank < card2.rank:
            return -1
          elif card1.rank > card2.rank:
            return 1
      
      # cards in hand are equal ranks
      return 0


  
@total_ordering
class Card:

  suits = {
    1: '♥',
    2: '♦',
    3: '♣',
    4: '♠'
  }
  ranks = {
    10: 'J',
    11: 'Q',
    12: 'K',
    13: 'A'
  }
  for i in range(2, 11):
    ranks[i - 1] = str(i)

  def __init__(self, rank, suit):
    self.rank = rank
    self.suit = suit
  
  def __repr__(self):
    return Card.ranks[self.rank] + Card.suits[self.suit]

  def __key(self):
    return (self.rank, self.suit)

  def __eq__(x, y):
    return x.__key() == y.__key()

  def __lt__(x, y):
    x_rank, x_suit = x.__key()
    y_rank, y_suit = y.__key()
    if x_rank < y_rank:
      return True
    else:
      return x_rank == y_rank and x_suit < y_suit

  def __hash__(self):
    return hash(self.__key())

    

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
