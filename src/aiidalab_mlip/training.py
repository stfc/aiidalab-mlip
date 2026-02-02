"""MLIP model selection wizard step."""

import aiidalab_widgets_base as awb
import ipywidgets as ipw
import traitlets


class TrainingWizardStep(ipw.VBox, awb.WizardAppWidgetStep):
    """Wizard step for MLIP model selection."""

    def __init__(self, model, **kwargs):
        """
        Initialize model selection wizard step.

        Parameters
        ----------
        model : TrainingModel
            The training data model
        """
        self.model = model

        self.title = ipw.HTML("<h3>Step 2: Select MLIP Model</h3>")
        
        self.mode_selector = ipw.ToggleButtons(
            options=[
                ('Use Pre-trained Model', 'pretrained'),
                ('Train Custom Model', 'train')
            ],
            value='pretrained',
            description='Mode:',
            button_style='info'
        )
        self.mode_selector.observe(self._on_mode_change, names='value')
        
        # Pre-trained model selection
        self.pretrained_selector = ipw.Dropdown(
            options=[
                ('MACE-MP-0 (small) - Fast, general materials', 'mace_mp_small'),
                ('MACE-MP-0 (medium) - Balanced', 'mace_mp_medium'),
                ('MACE-MP-0 (large) - Accurate, slow', 'mace_mp_large'),
            ],
            value='mace_mp_small',
            description='Pre-trained:',
            layout=ipw.Layout(width='500px')
        )
        
        self.pretrained_info = ipw.HTML(
            """
            <p><b>Pre-trained models</b> are ready to use immediately.</p>
            <p>MACE-MP-0 models are trained on the Materials Project database
            and work well for general materials screening.</p>
            <p>✓ No training data required<br>
            ✓ Fast setup<br>
            ✓ Good for initial exploration</p>
            """
        )
        
        # Training section
        self.model_type_selector = ipw.Dropdown(
            options=['MACE', 'M3GNET', 'CHGNET'],
            value='MACE',
            description='Architecture:',
        )
        
        self.training_info = ipw.HTML(
            """
            <p><b>Custom training</b> requires your own training data.</p>
            <p>You need:</p>
            <ul>
                <li>Training dataset (XYZ format with energies/forces)</li>
                <li>Validation dataset</li>
                <li>Test dataset (optional)</li>
            </ul>
            <p>Training can take hours to days depending on data size.</p>
            """
        )
        
        self.train_button = ipw.Button(
            description='Configure Training',
            button_style='warning',
            disabled=False
        )
        self.train_button.on_click(self._on_train_click)
        
        self.continue_button = ipw.Button(
            description='Continue with Pre-trained Model →',
            button_style='success',
            disabled=False
        )
        self.continue_button.on_click(self._on_continue_click)
        
        self.status = ipw.HTML()
        self.output = ipw.Output()
        
        # Container for mode-specific widgets
        self.mode_area = ipw.VBox()
        self._update_mode_area()

        super().__init__(
            children=[
                self.title,
                self.mode_selector,
                self.mode_area,
                self.status,
                self.output
            ],
            **kwargs
        )
    
    def _on_mode_change(self, change):
        """Handle mode selection change."""
        self._update_mode_area()
    
    def _update_mode_area(self):
        """Update the displayed widgets based on selected mode."""
        if self.mode_selector.value == 'pretrained':
            self.mode_area.children = [
                self.pretrained_info,
                self.pretrained_selector,
                self.continue_button
            ]
            self.model.model_type = 'MACE'
            self.status.value = "<p style='color: green;'>✓ Ready to use pre-trained model</p>"
        else:
            self.mode_area.children = [
                self.training_info,
                self.model_type_selector,
                self.train_button
            ]
            self.status.value = "<p style='color: orange;'>⚠ Training setup required</p>"
    
    def _on_continue_click(self, button):
        """Handle continue with pre-trained model."""
        model_name = self.pretrained_selector.value
        with self.output:
            self.output.clear_output()
            print(f"✓ Selected pre-trained model: {model_name}")
            print("\nThis model will be automatically downloaded when you run calculations in Step 3.")
            print("You can now proceed to Step 3 to run predictions!")
        
        self.status.value = f"<p style='color: green;'>✓ Using {model_name}</p>"
    
    def _on_train_click(self, button):
        """Handle train button click."""
        with self.output:
            self.output.clear_output()
            print("⚠ Custom training is not yet implemented in the web interface.")
            print()
            print("To train a custom MLIP model, you can use the aiida-mlip Python API:")
            print()
            print("1. Prepare your training data in XYZ format with energy/force labels")
            print()
            print("2. Create a training configuration:")
            print("```python")
            print("from aiida import orm, engine")
            print("from aiida_mlip.calculations.train import Train")
            print("from aiida_mlip.data.config import JanusConfigfile")
            print()
            print("config = JanusConfigfile({")
            print("    'name': 'my_model',")
            print("    'train_file': 'train.xyz',")
            print("    'valid_file': 'valid.xyz',")
            print("    'arch': 'mace',")
            print("    'energy_weight': 1.0,")
            print("    'forces_weight': 10.0,")
            print("})")
            print()
            print("builder = Train.get_builder()")
            print("builder.code = orm.load_code('janus@localhost')")
            print("builder.mlip_config = config")
            print("node = engine.submit(builder)")
            print("```")
            print()
            print("3. Monitor training with: verdi process list")
            print()
            print("For now, continue with a pre-trained model!")
            
            self.status.value = "<p style='color: orange;'>⚠ Use pre-trained models or Python API for training</p>"
