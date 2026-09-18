import ipywidgets as ipw

template = """
<table>
<tr>
  <th style="text-align:center"> Machine Learning Interatomic Potentials (MLIP)</th>
<tr>
  <td valign="top"><ul>
    <li><a href="{appbase}/main.ipynb" target="_blank">Launch MLIP App</a></li>
    <!-- <li><a href="{appbase}/train.ipynb" target="_blank">Train and deploy
ML potentials for molecular simulations</a></li> -->
  </ul></td>
</tr>
</table>
"""


def get_start_widget(appbase, jupbase, notebase):
    html = template.format(appbase=appbase, jupbase=jupbase, notebase=notebase)
    return ipw.HTML(html)


# EOF
