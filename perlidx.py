import sublime, sublime_plugin, re, time

views = {}

def DisplayCurrentSub(view, subs, index, pos):
    views[view.id()]['last'] = { 'index': index, 'pos': pos }

    if index > -1:
        view.set_status('perlsubs', '[PerlSub: '+subs[index][2]+']')
    else:
        if IsPerl(view):
            view.set_status('perlsubs', '[PerlSub: <none>]')

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
    
    DisplayCurrentSub(view, subs, index, pos)

def IsPerl(view):
    syntax = view.settings().get('syntax')
    if syntax == 'Packages/Perl/Perl.tmLanguage':
        return 1
    elif syntax == 'Packages/ModernPerl/ModernPerl.tmLanguage':
        return 1
    elif syntax == 'Packages/Perl/Perl.sublime-syntax':
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
    last_scaned = view_rec['last_scaned']
    if (t < last_scaned) or (changed > t):
        return
    else:
        subs = get_subs_list(view)
        GetCurrentSub(view, subs)


class PerlIndexView(sublime_plugin.EventListener):

    def on_new(self, view):
        views[view.id()] = { 'subs' : [], 'last_scaned' : 0, 'changed': 0 }
    def on_load(self, view):
        self.on_modified(view)
    def on_close(self, view):
        if view.id() in views:
            del views[view.id()]
    def on_modified(self, view):
        t = time.time()
        if view.id() not in views:
            views[view.id()] = { 'subs' : [], 'last_scaned' : 0, 'changed': 0 }
        views[view.id()]['changed'] = t
        func = lambda: deferred_get_list(view, t)
        sublime.set_timeout(func, 2000)
    def on_selection_modified(self, view):
        if not (view.id() in views):
            self.on_modified(view)
            return
        subs = views[view.id()]['subs']
        if len(subs) == 0:
            return
        GetCurrentSub(view, subs)

class PerlSubsCommand(sublime_plugin.TextCommand):  
    def run(self, edit):
        view = self.view
        subs = None;
        if not (view.id() in views):
            subs = get_subs_list(view)
        else:
            subs = views[view.id()]['subs']
        if len(subs) == 0:
            return
        if 'last' not in views[view.id()]:
            GetCurrentSub(view, subs)
        index = views[view.id()]['last']['index']
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
        pos = rec[1]
        view.show_at_center(pos)
        view.sel().clear()
        view.sel().add(sublime.Region(pos, pos))
        DisplayCurrentSub(view, subs, arg, pos)
