import sublime, sublime_plugin, re

views = {}

def GetCurrentSub(view, subs):
    pos = view.sel()[0].begin()
    index = -1
    for r in subs:
        if r[1] <= pos:
            index = index + 1
        else:
            break
    return index

def IsPerl(view):
    if view.settings().get('syntax') == 'Packages/Perl/Perl.tmLanguage':
        return 1
    else:
        return 0

def get_subs_list(view):
    if not IsPerl(view):
        return []
    regions = view.find_all(r"\bsub\s+\w+\s*\{");
    subs = [];
    for r in regions:
        if view.syntax_name(r.begin()).find('storage.type.sub.perl') >= 0:
            m = re.match(r"sub\s+(\w+)\s*\{", view.substr(r))
            name = m.group(1)
            subs.append([name, r.begin()])
    return subs

class PerlIndexView(sublime_plugin.EventListener):

    def on_new(self, view):
        views[view.id()] = []
    def on_load(self, view):
        views[view.id()] = get_subs_list(view)
    def on_close(self, view):
        if view.id() in views:
            del views[view.id()]
    def on_modified(self, view):
        views[view.id()] = get_subs_list(view)
    def on_selection_modified(self, view):
        if not (view.id() in views):
            views[view.id()] = get_subs_list(view)
        subs = views[view.id()]
        if len(subs) == 0:
            return
        index = GetCurrentSub(view, subs)
        if index > -1:
            view.set_status('perlsubs', '[PerlSub: '+subs[index][0]+']')
        else:
            view.set_status('perlsubs', '[PerlSub: <none>]')

class PerlSubsCommand(sublime_plugin.TextCommand):  
    def run(self, edit):
        view = self.view
        if not (view.id() in views):
            views[view.id()] = get_subs_list(view)
        subs = views[view.id()]
        if len(subs) > 0:
            index = GetCurrentSub(view, subs)
            view.window().show_quick_panel([s[0] for s in subs], self.jumpto, 0, index)
    def jumpto(self, arg):
        if arg < 0:
            return
        view = self.view
        if not (view.id() in views):
            views[view.id()] = get_subs_list(view)
        subs = views[view.id()]
        rec = subs[arg]
        view.show_at_center(rec[1])
        

# http://www.sublimetext.com/docs/2/api_reference.html
# http://docs.sublimetext.info/en/latest/reference/snippets.html

# view.window().show_quick_panel(display_args, callback, <flags>, <default select>)
# display_args is a list of strings or list of list of strigs

# Window function
# ['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', 
# '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 
# 'active_group', 'active_view', 'active_view_in_group', 'find_open_file', 'focus_group', 'focus_view', 'folders', 'get_layout',
#  'get_output_panel', 'get_view_index', 'id', 'new_file', 'num_groups', 'open_file', 'run_command', 'set_layout', 'set_view_index', 
#  'show_input_panel', 'show_quick_panel', 'views', 'views_in_group']

# Perl syntax names
# [u'', u'string.regexp.replaceXXX.simple_delimiter.perl', u'keyword.operator.logical.perl', u'string.regexp.find-m.perl', 
# u'string.regexp.replaceXXX.format.simple_delimiter.perl', u'punctuation.definition.variable.perl', u'entity.name.function.perl',
# u'string.regexp.replace.perl', u'storage.modifier.perl', u'constant.character.escape.perl', u'comment.line.number-sign.perl', 
# u'meta.odd-tab', u'storage.type.sub.perl', u'source.perl', u'meta.function.perl', u'meta.leading-tabs', u'meta.comment.full-line.perl',
#  u'constant.other.key.perl', u'punctuation.definition.string.begin.perl', u'keyword.control.perl',
#   u'punctuation.definition.string.perl', u'keyword.operator.comparison.perl', u'keyword.control.regexp-option.perl', 
#   u'punctuation.definition.string.end.perl', u'support.function.perl', u'comment.block.documentation.perl', 
#   u'string.unquoted.program-block.perl', u'meta.class.perl', u'entity.name.type.class.perl', u'string.quoted.single.perl', 
#   u'variable.other.readwrite.global.special.perl', u'string.quoted.double.perl', u'punctuation.definition.comment.perl',
#    u'meta.even-tab', u'variable.other.readwrite.global.perl']


# view dir
# ['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', 
# '__init__', '__len__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__',
#  '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'add_regions', 'begin_edit', 'buffer_id',
#   'classify', 'command_history', 'em_width', 'encoding', 'end_edit', 'erase', 'erase_regions', 
#   'erase_status', 'extract_completions', 'extract_scope', 'file_name', 'find', 'find_all', 
#   'find_by_selector', 'fold', 'folded_regions', 'full_line', 'get_regions', 'get_status', 
#   'get_symbols', 'has_non_empty_selection_region', 'id', 'indentation_level', 'indented_region',
#    'insert', 'is_dirty', 'is_folded', 'is_loading', 'is_read_only', 'is_scratch', 'layout_extent',
#     'layout_to_text', 'line', 'line_endings', 'line_height', 'lines', 'match_selector', 'meta_info',
#      'name', 'replace', 'retarget', 'rowcol', 'run_command', 'scope_name', 'score_selector', 'sel', 
#      'set_encoding', 'set_line_endings', 'set_name', 'set_read_only', 'set_scratch', 'set_status', 
#      'set_syntax_file', 'set_viewport_position', 'settings', 'show', 'show_at_center', 'size', 
#      'split_by_newlines', 'substr', 'syntax_name', 'text_point', 'text_to_layout', 'unfold', 
#      'viewport_extent', 'viewport_position', 'visible_region', 'window', 'word']
