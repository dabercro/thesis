#! /usr/bin/env python

import sys
from collections import defaultdict

sys.path.append('/home/dabercro/GradSchool/VHLegacy/python')

import misc

datacardname = sys.argv[1]

binorder = None
processorder = None
processnumorder = None
observations = None
simulations = defaultdict(dict)

with open(datacardname, 'r') as inputfile:
    for line in inputfile:

        if line.startswith('bin '):
            binorder = line.split()[1:]

        elif line.startswith('observation '):
            observations = {
                binname: value.split('.')[0] \
                for binname, value in \
                zip(binorder, line.split()[1:])
            }

        elif line.startswith('process '):
            if processorder is None:
                processorder = line.split()[1:]
            else:
                processnumorder = [int(num) for num in line.split()[1:]]

        elif line.startswith('rate '):
            for i, entry in enumerate(line.split()[1:]):
                simulations[binorder[i]][processorder[i]] = '{:.3e}'.format(float(entry))

signals = set()
backgrounds = set()

for process, num in zip(processorder, processnumorder):
    if num > 0:
        backgrounds.add(process)
    else:
        signals.add(process)

outlines = [r'\chapter{Data Card} \label{app:datacard}', '',
            '''
            The tables in this appendix give the observed yields
            and prefit predictions for each channel and each year.
            ''']

def add_table(rows, caption, abbr, label):
    global outlines
    outlines += [
        r'\begin{table}',
        r'\centering',
        r'\caption[' + abbr + ']{' + caption + '}',
        r'{\footnotesize',
        r'\begin{tabularx}{' + ('' if len(rows[0]) > 4 else '0.8') + r'\textwidth}{|' + '|'.join(['X' for _ in rows[0]]) + '|}',
        r'\hline',
    ] + [
        ' & '.join(row) + r' \\' if row else r'\hline' \
        for row in rows if not row or False in [entry == '0' for entry in row[1:]]
    ] + [
        r'\hline',
        r'\end{tabularx}',
        r'}',
        r'\label{tab:' + label + '}',
        r'\end{table}', ''
    ]

def process_label(label):
    output = label.replace('p_{T}(V)', '$p_{T}(V)$')
    output = output.replace('#', '\\')
    output = output.replace('b\\bar{b}', '$b\\bar{b}$')
    output = output.replace('t\\bar{t}', '$t\\bar{t}$')
    return output

def process_process(process):
    output = process.replace('lep_PTV_', '')
    output = output.replace('H_', 'H ')
    output = output.replace('_0', ' 0')
    output = output.replace('_GE', ' GE')
    output = output.replace('_hbb', '')
    output = output.replace('_', '\\_')
    return output

for _, year in misc.LUMI_YEAR:
    for chn, chn_label in misc.CHANNELS:

        label = chn_label.replace('#', '\\')
        label = label.replace('(', '($')
        label = label.replace(')', '$)')

        # Signal table
        signal_bins = misc.Bins(chn, signals=True)

        bin_template = 'vhbb_' + chn + '_%s_13TeV' + year

        rows = [['Process'] + [process_label(misc.BinLabel(binnum, chn)) for binnum in signal_bins], []] + \
            [['Data'] + [observations[bin_template % binnum] for binnum in signal_bins]] + [[]] + \
            [[process_process(procname)] + [simulations[bin_template % binnum].get(procname, '0') for binnum in signal_bins] for procname in sorted(signals)] + [[]] + \
            [[process_process(procname)] + [simulations[bin_template % binnum].get(procname, '0') for binnum in signal_bins] for procname in sorted(backgrounds)]
        
        add_table(rows,
                  '''
                  The observed and predicted yields are given for the
                  signal regions for %s in %s.
                  ''' % (label, year),
                  year + ' ' + label + ' signal selection yields',
                  'sr-' + chn + '-' + year)

        # Background table
        background_bins = misc.Bins(chn, backgrounds=True)

        lf = [binnum for binnum in background_bins if 'udcsg' in misc.BinLabel(binnum, chn)]
        hf = [binnum for binnum in background_bins if 'b#bar{b}' in misc.BinLabel(binnum, chn)]
        tt = [binnum for binnum in background_bins if 't#bar{t}' in misc.BinLabel(binnum, chn)]

        rows = [['Process'] + [process_label(misc.BinLabel(binnum, chn)) for binnum in lf], []] + \
            [['Data'] + [observations[bin_template % binnum] for binnum in lf]] + [[]] + \
            [[process_process(procname)] + [simulations[bin_template % binnum].get(procname, '0') for binnum in lf] for procname in sorted(backgrounds)] + \
            [[], [], ['Process'] + [process_label(misc.BinLabel(binnum, chn)) for binnum in hf], []] + \
            [['Data'] + [observations[bin_template % binnum] for binnum in hf]] + [[]] + \
            [[process_process(procname)] + [simulations[bin_template % binnum].get(procname, '0') for binnum in hf] for procname in sorted(backgrounds)] + \
            [[], [], ['Process'] + [process_label(misc.BinLabel(binnum, chn)) for binnum in tt], []] + \
            [['Data'] + [observations[bin_template % binnum] for binnum in tt]] + [[]] + \
            [[process_process(procname)] + [simulations[bin_template % binnum].get(procname, '0') for binnum in tt] for procname in sorted(backgrounds)]

        add_table(rows,
                  '''
                  The observed and predicted yields are given for the
                  control regions for %s in %s.
                  ''' % (label, year),
                  year + ' ' + label + ' control region yields',
                  'cr-' + chn + '-' + year)

print('\n'.join(outlines))
