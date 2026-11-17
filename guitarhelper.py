"""
Chord Helper

Displays exact or closest chords to the notes user selects.

Vibe-coding/AI usage disclaimer

Features:
- 3 octave piano keyboard
- Exact chord matches
- Slash chord detection
- Nearby chords
- Nearby inverted chords
- Click nearby chord to audition/select
- Scrollable chord rows
- Large chord vocabulary including 9th/11th/13th variants
- Basic voice-leading when loading nearby chords
"""
import tkinter as tk
from tkinter import ttk

NOTE_NAMES=["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
CHORD_TYPES={
"": [0,4,7], "m":[0,3,7], "dim":[0,3,6], "aug":[0,4,8],
"sus2":[0,2,7],"sus4":[0,5,7],"6":[0,4,7,9],"m6":[0,3,7,9],
"7":[0,4,7,10],"maj7":[0,4,7,11],"m7":[0,3,7,10],
"m7b5":[0,3,6,10],"dim7":[0,3,6,9],
"add9":[0,2,4,7],"madd9":[0,2,3,7],
"9":[0,4,7,10,14],"maj9":[0,4,7,11,14],"m9":[0,3,7,10,14],
"11":[0,4,7,10,14,17],"13":[0,4,7,10,14,21]
}
ALL=[]
for r in range(12):
    for s,i in CHORD_TYPES.items():
        ALL.append({"root":r,"name":NOTE_NAMES[r]+s,"intervals":i,"pcs":frozenset((r+x)%12 for x in i)})

class App:
    def __init__(self,root):
        self.root=root
        root.title('Chord Helper')
        root.geometry('1400x850')
        self.selected=set()
        self.keys={}
        self.black=set()

        self.header=tk.Label(root,font=('Segoe UI',18,'bold'),anchor='w')
        self.header.pack(fill='x',padx=10,pady=5)

        self.keyboard=tk.Canvas(root,height=260,bg='#8f8f8f')
        self.keyboard.pack(fill='x',padx=10)
        self.draw_keyboard()

        self.row1=self.make_scroll_row('Nearby Chords')
        self.row2=self.make_scroll_row('Nearby Inverted Chords')
        self.refresh()

    def make_scroll_row(self,title):
        frame=ttk.LabelFrame(self.root,text=title)
        frame.pack(fill='x',padx=10,pady=5)
        c=tk.Canvas(frame,height=90)
        s=ttk.Scrollbar(frame,orient='horizontal',command=c.xview)
        c.configure(xscrollcommand=s.set)
        inner=tk.Frame(c)
        c.create_window((0,0),window=inner,anchor='nw')
        inner.bind('<Configure>',lambda e,c=c:c.configure(scrollregion=c.bbox('all')))
        c.pack(fill='x'); s.pack(fill='x')
        return inner

    def draw_keyboard(self):
        white=['C','D','E','F','G','A','B']
        x=10; midi=48; pos={}
        notes=[]
        m=midi
        for _ in range(3):
            for n in white:
                notes.append((n,m)); m += 2 if n not in ('E','B') else 1
        for name,n in notes:
            r=self.keyboard.create_rectangle(x,20,x+45,240,fill='white')
            self.keyboard.create_text(x+22,220,text=f'{name}{n//12-1}')
            self.keys[n]=r; pos[n]=x
            self.keyboard.tag_bind(r,'<Button-1>',lambda e,k=n:self.toggle(k))
            x+=45
        for base,x in pos.items():
            if base%12 in [0,2,5,7,9]:
                b=base+1
                if b<84:
                    r=self.keyboard.create_rectangle(x+30,20,x+58,140,fill='black')
                    self.keys[b]=r; self.black.add(b)
                    self.keyboard.tag_bind(r,'<Button-1>',lambda e,k=b:self.toggle(k))

    def toggle(self,n):
        if n in self.selected:self.selected.remove(n)
        else:self.selected.add(n)
        self.refresh()

    def exact_matches(self):
        if not self.selected:return []
        pcs=frozenset(n%12 for n in self.selected)
        bass=min(self.selected)%12
        out=[]
        for c in ALL:
            if c['pcs']==pcs:
                lbl=c['name']
                if bass!=c['root']: lbl += '/' + NOTE_NAMES[bass]
                out.append(lbl)
        return sorted(set(out))

    def best_match(self):
        pcs=frozenset(n%12 for n in self.selected)
        best=None; score=-1e9
        for c in ALL:
            s=len(pcs & c['pcs'])*10-len(pcs-c['pcs'])*4-len(c['pcs']-pcs)*4
            if s>score: score=s; best=c['name']
        return best

    def nearby(self):
        pcs=frozenset(n%12 for n in self.selected)
        out=[]
        for c in ALL:
            d=len(pcs.symmetric_difference(c['pcs']))
            if d<=2: out.append((d,c))
        return sorted(out,key=lambda x:(x[0],x[1]['name']))[:80]

    def load_chord(self,c,bass=None):
        self.selected.clear()
        root=48+c['root']
        notes=[root+i for i in c['intervals']]
        while max(notes)>83:
            notes=[n-12 for n in notes]
        if bass is not None:
            for i,n in enumerate(notes):
                if n%12==bass:
                    while n>=min(notes): n-=12
                    notes[i]=n
                    break
        self.selected.update(notes)
        self.refresh()

    def refresh(self):
        for n,item in self.keys.items():
            self.keyboard.itemconfig(item,fill='#3fa9ff' if n in self.selected else ('black' if n in self.black else 'white'))

        m=self.exact_matches()
        self.header.config(text=', '.join(m) if m else ('Closest Match: '+self.best_match() if self.selected else 'Select notes'))

        for row in [self.row1,self.row2]:
            for w in row.winfo_children(): w.destroy()

        for d,c in self.nearby():
            tk.Button(self.row1,text=f"{c['name']}\n{d} away",command=lambda cc=c:self.load_chord(cc)).pack(side='left',padx=3,pady=3)

        inv=[]
        for d,c in self.nearby():
            for pc in sorted(c['pcs']):
                if pc!=c['root']:
                    inv.append((d,c,pc))
        for d,c,pc in inv[:120]:
            tk.Button(self.row2,text=f"{c['name']}/{NOTE_NAMES[pc]}",command=lambda cc=c,b=pc:self.load_chord(cc,b)).pack(side='left',padx=3,pady=3)

root=tk.Tk()
App(root)
root.mainloop()
