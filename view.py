import sys

class View:
  def __init__(self):
    for _ in range(1000):
      print('') # put UI at bottom of console

  def clear_console(self):
    return chr(27) + "[2J\n"

  def render(self, model):
    hand_rank_names = {rank:name for rank,name in zip(model.hand_ranks, [
      'straight-flush',
      '4 of a kind',
      'full-house',
      'flush',
      'straight',
      '3 of a kind',
      '2 pair',
      'pair',
      'high card'
    ])}

    def highlight(text, color):
      color_num = {
        'red': 41,
        'green': 42,
        'blue': 44,
        'gray': 47,
        'magenta': 45
      }
      return "\033[1;" + str(color_num[color]) + "m" + str(text) + "\033[1;m"

    def print_item(i, j, item):
      text = item.value

      if item.is_top_left:
        return ' '
      
      if model.cursor[0] == i and model.cursor[1] == j:
        if item.is_selected and not (item.card in model.player_hand.hand or item.card in model.dealer_hand.hand):
          text = highlight(text, 'blue')
        else:
          text =  highlight(text, 'red')
      elif item.is_card and item.card in model.dealer_hand.hand:
        text = highlight(text, 'gray')
      elif item.is_card and item.card in model.player_hand.hand:
        text = highlight(text, 'magenta')
      elif item.is_selected:
        text = highlight(text, 'green')

      if item.is_card:
        text = '|' + text + '|'
      if item.is_top_row:
        text = ' ' + text + '  '

      return text

    render_lines = []        

    def render_title():
      render_lines.append(
'''
RENJAY POKER is a solitare poker variant.

Select which cards should be filtered to your hand if drawn.
Everything else will go to the dealer. The game is over once you
have 5 cards and the dealer has at least 8.

Whoever has the best 5-card poker hand by rank wins. The dealer wins
in the case of equal ranks regardless of the value of the suits.

To create your filter, either select cards individually or by rank
or suit using the top row and leftmost column.
'''
      )

    def render_filter_instructions():
      render_lines.append('-------------------------')
      render_lines.append('ARROW KEYS to move cursor\nSPACE to select\nENTER to start drawing')
      render_lines.append('-------------------------\n')

    def render_drawing_instructions():
      render_lines.append('-----------------------')
      render_lines.append('Drawing cards until one\nmatches the filter...')
      render_lines.append('-----------------------\n')

    def render_finishing_instructions():
      render_lines.append('--------------------------')
      render_lines.append('Drawing cards until dealer\nhas 8...')
      render_lines.append('--------------------------\n')

    def render_draw(draw):
      render_lines.append('Draw:')
      for card in draw[::-1]:
        render_lines.append(str(card))
      render_lines.append('')

    def render_hands(player_hand, dealer_hand):
      render_lines.append('Player: ' + ' '.join(map(str, player_hand)))
      render_lines.append('Dealer: ' + ' '.join(map(str, dealer_hand)))
      render_lines.append('')

    def render_selection_matrix(matrix):
      render_lines.append('Filter:')
      for i, item_list in enumerate(matrix):
        text_list = [print_item(i,j,item) for j, item in enumerate(item_list)]
        text = ' '.join(text_list)
        render_lines.append(text)

    def render_score(player_score, dealer_score):
      player_score_text = 'nothing'
      dealer_score_text = 'nothing'
      if player_score:
        player_hand_rank, player_cards = player_score
        player_cards = sorted(list(player_cards))
        player_score_text = hand_rank_names[player_hand_rank] + ' (' + ' '.join(map(str, player_cards)) + ')'
      if dealer_score:
        dealer_hand_rank, dealer_cards = dealer_score
        dealer_cards = sorted(list(dealer_cards))
        dealer_score_text = hand_rank_names[dealer_hand_rank] + ' (' + ' '.join(map(str, dealer_cards)) + ')'

      render_lines.append('\nScore:')
      render_lines.append('Player: ' + player_score_text)
      render_lines.append('Dealer: ' + dealer_score_text)


    if model.state == model.GameMode.FILTERING:
      if len(model.drawn_cards) > 0:
        render_draw(model.drawn_cards)
      else:
        render_title()
      render_filter_instructions()
      render_hands(model.player_hand.get_hand(), model.dealer_hand.get_hand())
      render_selection_matrix(model.selection_matrix)
      render_score(model.player_hand.score(), model.dealer_hand.score())
    
    elif model.state == model.GameMode.DRAWING:
      render_draw(model.drawn_cards)
      render_drawing_instructions()
      render_hands(model.player_hand.get_hand(), model.dealer_hand.get_hand())
      render_selection_matrix(model.selection_matrix)
      render_score(model.player_hand.score(), model.dealer_hand.score())

    elif model.state == model.GameMode.FINISHING:
      render_draw(model.drawn_cards)
      render_finishing_instructions()
      render_hands(model.player_hand.get_hand(), model.dealer_hand.get_hand())
      render_selection_matrix(model.selection_matrix)
      render_score(model.player_hand.score(), model.dealer_hand.score())
    
    if model.message:
      render_lines.append('\n' + model.message + '\n')


    render_text = self.clear_console() + '\n'.join(render_lines)

    sys.stdout.write(render_text)
    sys.stdout.flush()
