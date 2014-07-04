import sublime, sublime_plugin, re, time

views = {}

def GetCurrentSub(view, subs):
    pos = view.sel()[0].a
    index = -1
    if 'last' in views[view.id()]:
        cache = views[view.id()]['last']
        last_pos = cache['pos']
        index = cache['index']
        if pos == last_pos:
            return index
        if pos > last_pos:
            for ix in range(index+1, len(subs)):
                if subs[ix][1] <= pos:
                    index = index + 1
                else:
                    break
        else:
            for ix in reversed(range(0, index+1)):
                if subs[ix][1] > pos:
                    index = index - 1
                else:
                    break
    else:
        for r in subs:
            if r[1] <= pos:
                index = index + 1
            else:
                break
    views[view.id()]['last'] = { 'index': index, 'pos': pos }
    return index

def IsPerl(view):
    syntax = view.settings().get('syntax')
    if syntax == 'Packages/Perl/Perl.tmLanguage':
        return 1
    elif syntax == 'Packages/ModernPerl/ModernPerl.tmLanguage':
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
    views[view.id()] = { 'subs': subs, 'last_scaned': time.time(), 'changed':0 }
    return subs


def deferred_get_list(view, t):
    if not (view.id() in views):
        return
    view_rec = views[view.id()]
    changed = view_rec['changed']
    if time.time() > view_rec['last_scaned'] + 10:
        get_subs_list(view)
    elif changed > t:
        new_delay = changed + 2 - time.time()
        func = lambda: deferred_get_list(view, changed)
        sublime.set_timeout(func, new_delay)
    else:
        get_subs_list(view)


class PerlIndexView(sublime_plugin.EventListener):

    def on_new(self, view):
        views[view.id()] = { 'subs' : [], 'last_scaned' : 0, 'changed': 0 }
    def on_load(self, view):
        get_subs_list(view)
    def on_close(self, view):
        if view.id() in views:
            del views[view.id()]
    def on_modified(self, view):
        t = time.time()
        views[view.id()]['changed'] = t
        sublime.set_timeout(lambda: deferred_get_list(view, t), 2000)
    def on_selection_modified(self, view):
        subs = None
        if not (view.id() in views):
            subs = get_subs_list(view)
        else:
            subs = views[view.id()]['subs']
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
        subs = None;
        if not (view.id() in views):
            subs = get_subs_list(view)
        else:
            subs = views[view.id()]['subs']
        if len(subs) > 0:
            index = GetCurrentSub(view, subs)
            view.window().show_quick_panel([s[0] for s in subs], self.jumpto, 0, index)
    def jumpto(self, arg):
        if arg < 0:
            return
        view = self.view
        subs = None
        if not (view.id() in views):
            subs = get_subs_list(view)
        else:
            subs = views[view.id()]['subs']
        rec = subs[arg]
        view.show_at_center(rec[1])
        view.sel().clear()
        view.sel().add(sublime.Region(rec[1], rec[1]))
        
