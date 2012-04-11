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
    subs = [];
    package = '';
    for r in view.find_by_selector('entity.name.function.perl, entity.name.type.class.perl'):
        name = view.substr(r)
        if view.score_selector(r.begin(), 'entity.name.function.perl'):
            subs.append([name, r.begin(), package + name])
        else:
            name = re.sub(r'\W+$', '', name);
            package = name + '::'
            subs.append(['Package ' + name, r.begin(), package])
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
            view.set_status('perlsubs', '[PerlSub: '+subs[index][2]+']')
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
        
