from pathlib import Path

p = Path("index.html")
s = p.read_text(encoding="utf-8")

# Idempotent: the generated site is already patched on subsequent workflow runs.
if "RIFF_ENGINE_V23" in s:
    raise SystemExit(0)

old = """    function buildDurations(style, bars) {
      const rhythmPool = style.rhythms;
      let remaining = bars * 16;
      const durations = [];
      while (remaining > 0) {
        let pat = randomChoice(rhythmPool).slice();
        if (Math.random() < 0.25) pat = pat.reverse();
        for (const d of pat) {
          if (remaining <= 0) break;
          durations.push(Math.min(d, remaining));
          remaining -= Math.min(d, remaining);
        }
      }
      return durations;
    }"""

new = r'''    // ===================== RIFF ENGINE V23 =====================
    // Genre DNA: density, rests, syncopation, chromatic colour, register,
    // repetition and variation are controlled per subgenre instead of using
    // one generic random-note algorithm.
    const RIFF_DNA_V23 = {
      thrash:{d:.92,r:.04,s:.42,c:.38,t:.08,m:.25,low:.82,up:.18,rep:.48,p:.72,mut:.55},
      thrash_gallop:{d:.96,r:.02,s:.22,c:.30,t:.05,m:.18,low:.90,up:.10,rep:.60,p:.78,mut:.25},
      death:{d:.90,r:.07,s:.55,c:.62,t:.28,m:.22,low:.90,up:.10,rep:.55,p:.52,mut:.68},
      melodeath:{d:.78,r:.04,s:.38,c:.20,t:.10,m:.82,low:.62,up:.38,rep:.38,p:.66,mut:.72},
      black:{d:.97,r:.01,s:.18,c:.18,t:.08,m:.72,low:.48,up:.52,rep:.78,p:.10,mut:.28},
      doom:{d:.25,r:.01,s:.10,c:.08,t:.68,m:.35,low:.96,up:.04,rep:.82,p:.92,mut:.20},
      stoner:{d:.48,r:.03,s:.48,c:.08,t:.20,m:.58,low:.88,up:.12,rep:.62,p:.84,mut:.42},
      groove:{d:.58,r:.10,s:.82,c:.20,t:.16,m:.28,low:.91,up:.09,rep:.55,p:.84,mut:.62},
      nu:{d:.45,r:.23,s:.90,c:.32,t:.12,m:.16,low:.97,up:.03,rep:.70,p:.66,mut:.45},
      metalcore:{d:.62,r:.18,s:.76,c:.18,t:.14,m:.52,low:.93,up:.07,rep:.52,p:.80,mut:.70},
      djent:{d:.55,r:.28,s:.97,c:.18,t:.34,m:.18,low:.98,up:.02,rep:.46,p:.72,mut:.82},
      progressive:{d:.72,r:.08,s:.62,c:.22,t:.22,m:.72,low:.52,up:.48,rep:.30,p:.56,mut:.90},
      deadsquad:{d:.91,r:.08,s:.72,c:.72,t:.48,m:.38,low:.68,up:.32,rep:.22,p:.42,mut:.94},
      polyphia:{d:.78,r:.04,s:.52,c:.10,t:.06,m:.94,low:.34,up:.66,rep:.22,p:.28,mut:.96},
      deathcore:{d:.42,r:.31,s:.94,c:.36,t:.50,m:.12,low:.995,up:.005,rep:.64,p:.66,mut:.56},
      hardcore:{d:.44,r:.26,s:.86,c:.24,t:.14,m:.12,low:.97,up:.03,rep:.74,p:.78,mut:.40},
      melodic_hc:{d:.66,r:.13,s:.70,c:.14,t:.10,m:.76,low:.76,up:.24,rep:.40,p:.74,mut:.78},
      modern_hc:{d:.52,r:.25,s:.94,c:.26,t:.20,m:.18,low:.98,up:.02,rep:.58,p:.74,mut:.64},
      thall:{d:.46,r:.38,s:1,c:.20,t:.78,m:.10,low:1,up:0,rep:.52,p:.58,mut:.92},
      power:{d:.74,r:.035,s:.34,c:.08,t:.04,m:.90,low:.48,up:.52,rep:.30,p:.62,mut:.86},
      brutal:{d:.64,r:.34,s:.97,c:.46,t:.58,m:.05,low:1,up:0,rep:.70,p:.52,mut:.55}
    };
    const riffDNA23 = id => RIFF_DNA_V23[id] || RIFF_DNA_V23.thrash;

    function buildDurations(style, bars) {
      const id = Object.keys(STYLE_DB).find(k => STYLE_DB[k] === style) || 'thrash';
      const dna = riffDNA23(id), out = [];
      for (let b=0; b<bars; b++) {
        let pat = randomChoice(style.rhythms).slice();
        if (id !== 'thrash_gallop' && Math.random() < dna.mut*.5)
          pat = pat.slice(Math.floor(Math.random()*pat.length)).concat(pat.slice(0,Math.floor(Math.random()*pat.length)));
        if (dna.d > .65 && Math.random() < dna.mut*.5) {
          const i = pat.findIndex(x => x >= 4);
          if (i >= 0) { const x=pat[i], a=Math.floor(x/2); pat.splice(i,1,a,x-a); }
        }
        if (dna.d < .42 && Math.random() < .7) {
          for (let i=0;i<pat.length-1;i++) if (pat[i]<=2 && pat[i+1]<=2) { pat.splice(i,2,pat[i]+pat[i+1]); break; }
        }
        let sum=pat.reduce((a,x)=>a+x,0);
        if(sum<16) pat.push(16-sum);
        if(sum>16) { let ex=sum-16; for(let i=pat.length-1;i>=0&&ex;i--){const cut=Math.min(ex,Math.max(0,pat[i]-1));pat[i]-=cut;ex-=cut;} }
        out.push(...pat.filter(Boolean));
      }
      return out;
    }

    function generateRhythm(opts) {
      const {key,scaleKey,styleId,style,bars,tuningKey,usePower,useAlt,useDown,usePalm,usePinch,useHopo,useSlide,durations}=opts;
      const dna=riffDNA23(styleId), open=TUNINGS[tuningKey], nstr=open.length, root=NOTE_TO_SEMI[key];
      const scale=SCALES[scaleKey]||SCALES.natural_minor, scalePC=getScaleNotes(key,scaleKey), pools=motifPoolsFor(styleId);
      const ultraLow=['deathcore','hardcore','modern_hc','thall','brutal','nu'];
      const events=[]; let step=0, down=true, di=0;

      const fret=(s,pc,max=17)=>{
        const hits=[]; for(let f=0;f<=max;f++) if((open[s]+f)%12===pc) hits.push(f);
        if(!hits.length) return 0;
        return hits[Math.floor(Math.random()*Math.min(4,hits.length))];
      };
      const fifth=(s,f)=>{
        if(s>=nstr-1)return null; const pc=(open[s]+f+7)%12;
        for(let x=0;x<=10;x++)if((open[s+1]+x)%12===pc)return{string:s+1,fret:x,midi:open[s+1]+x};
        return null;
      };
      const pickString=()=>{
        const r=Math.random();
        if(r<dna.low/(dna.low+dna.up+.35)) return Math.random()<.86?0:Math.min(1,nstr-1);
        if(r<(dna.low+dna.up)/(dna.low+dna.up+.35)) return Math.min(nstr-1,1+Math.floor(Math.random()*Math.max(1,nstr-2)));
        return Math.min(nstr-1,Math.floor(nstr/2)+Math.floor(Math.random()*Math.max(1,nstr-Math.floor(nstr/2))));
      };
      const makeBar=(count,bar)=>{
        const pool=randomChoice(pools), a=randomChoice(pool).slice(), b=randomChoice(pool).slice(), out=[];
        let src=(bar===0||Math.random()<dna.rep)?a:b;
        while(out.length<count){
          let m=(Math.random()<dna.mut*.35)?b:src, seq=m.slice();
          if(Math.random()<dna.mut*.35)seq.reverse();
          for(const raw of seq){
            if(out.length>=count)break;
            let q=raw;
            if(dna.c<.45 && !scale.includes(q%12)) q=quantizeToScale(q,scale);
            if(dna.m>0.7 && Math.random()<.20) q=randomChoice(scale.filter(x=>x!==0));
            if(Math.random()<dna.c*.14) q=randomChoice([1,6,10,11]);
            if(dna.t>.5 && Math.random()<dna.t*.35) q=6;
            out.push((root+q+12)%12);
          }
          src=(src===a?b:a);
        }
        if(out.length){if(bar===0||Math.random()<.7)out[0]=root;if(bar===bars-1)out[out.length-1]=root;}
        return out;
      };

      for(let bar=0;bar<bars;bar++){
        const start=di; let sum=0;
        while(di<durations.length&&sum<16){sum+=durations[di++];}
        const ds=durations.slice(start,di), pcs=makeBar(ds.length,bar);
        for(let j=0;j<ds.length;j++){
          const dur=ds[j], pos=step%16, accent=[0,4,8,12].includes(pos), off=[2,6,10,14].includes(pos), hard=[3,7,11,15].includes(pos);
          let rc=dna.r*(accent?.45:1);
          if(styleId==='doom'||styleId==='stoner'||styleId==='black')rc*=.25;
          if((styleId==='djent'||styleId==='thall')&&hard)rc*=.65;
          if(Math.random()<rc&&j>0&&j<ds.length-1){events.push({notes:[],dur,rest:true,pick:null,muted:false,power:false,tech:null});step+=dur;continue;}

          let pc=pcs[j];
          if(['djent','thall','deathcore','brutal'].includes(styleId)&&(accent||hard)&&Math.random()<.72)pc=root;
          if(styleId==='nu'&&!accent&&Math.random()<.72)pc=root;
          if(styleId==='hardcore'&&!accent&&Math.random()<.58)pc=root;
          if(styleId==='groove'&&off&&Math.random()<.48)pc=(root+randomChoice([0,3,7,10]))%12;
          if(styleId==='doom'&&Math.random()<.4)pc=(root+6)%12;
          if(styleId==='thall'&&Math.random()<.55)pc=randomChoice([root,(root+1)%12,(root+6)%12,(root+11)%12]);

          let s=pickString();
          if(ultraLow.includes(styleId)||styleId==='doom')s=Math.random()<.93?0:Math.min(1,nstr-1);
          if(styleId==='black'&&Math.random()<dna.up)s=Math.min(nstr-1,2+Math.floor(Math.random()*Math.max(1,nstr-2)));
          if(['power','polyphia','progressive','melodeath'].includes(styleId)&&Math.random()<dna.up)s=Math.min(nstr-1,2+Math.floor(Math.random()*Math.max(1,nstr-2)));

          const prev=events.length?events[events.length-1]:null;
          if(prev?.notes?.length&&Math.random()<.5&&!['djent','thall','deadsquad','polyphia'].includes(styleId))
            s=Math.max(0,Math.min(nstr-1,prev.notes[0].string+(Math.random()<.5?-1:1)));

          const max=ultraLow.includes(styleId)||['doom','deathcore','thall'].includes(styleId)?5:(['power','progressive','polyphia','melodeath'].includes(styleId)?15:8);
          let f=fret(s,pc,max), actual=(open[s]+f)%12;
          if(scaleKey!=='chromatic'&&!scalePC.includes(actual)&&dna.c<.45){const safe=randomChoice(scalePC);f=fret(s,safe,max);pc=safe;}

          const rootish=pc===root||pc===(root+7)%12||pc===(root+5)%12;
          let pp=dna.p*(rootish?1.18:.55); if(s>=2)pp*=.3; if(dna.m>.7)pp*=.5;
          const isPower=usePower&&rootish&&Math.random()<Math.min(1,pp), notes=[{string:s,fret:f,midi:open[s]+f}];
          if(isPower){const x=fifth(s,f);if(x)notes.push(x);}

          let pick=styleId==='black'?'T':(useDown?'D':(useAlt?(down?'D':'U'):'D')); if(useAlt)down=!down;
          let muted=false;
          if(usePalm&&!['doom','stoner','black','polyphia','power'].includes(styleId))
            muted=Math.random()<Math.min(.9,.25+dna.s*.48) && dur<4;

          let tech=null;
          if(usePinch&&!muted&&(accent||hard)&&dur>=2&&Math.random()<.035)tech='ph';
          if(useHopo&&prev?.notes?.length&&prev.notes[0].string===s&&!tech){
            const df=f-prev.notes[0].fret;if(Math.abs(df)<=2&&Math.abs(df)>=1&&Math.random()<(dna.m>.65?.2:.1))tech=df>0?'h':'p';
          }
          if(useSlide&&prev?.notes?.length&&prev.notes[0].string===s&&!tech){
            const df=f-prev.notes[0].fret;if(Math.abs(df)>=3&&Math.random()<.1)tech=df>0?'/':'\\\\';
          }
          if(dna.m>.7&&styleId==='deadsquad'&&Math.random()<.08)tech='x';

          events.push({notes,dur,rest:false,pick,muted,power:isPower&&notes.length>1,tech,crossed:!!(prev?.notes?.length&&prev.notes[0].string!==s)});
          step+=dur;
        }
      }
      return events;
    }'''

if old not in s:
    raise SystemExit("buildDurations block not found")
s=s.replace(old,new,1)
marker="    function generateRhythm(opts) {"
s=s.replace(marker, "    // RIFF_ENGINE_V23\n"+marker, 1)
p.write_text(s,encoding="utf-8")

import subprocess
subprocess.run(["git","config","user.name","github-actions[bot]"],check=False)
subprocess.run(["git","config","user.email","41898282+github-actions[bot]@users.noreply.github.com"],check=False)
subprocess.run(["git","add","index.html"],check=False)
subprocess.run(["git","diff","--cached","--quiet"],check=False)
