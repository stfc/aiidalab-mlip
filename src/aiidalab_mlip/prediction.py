"""MLIP prediction wizard step."""

import aiidalab_widgets_base as awb
import ipywidgets as ipw
import traitlets

try:
    from aiida import orm, engine
    from aiida_mlip.calculations.geomopt import GeomOpt
    from aiida_mlip.calculations.singlepoint import Singlepoint
    from aiida_mlip.data.model import ModelData
    AIIDA_MLIP_AVAILABLE = True
except ImportError:
    AIIDA_MLIP_AVAILABLE = False


class PredictionWizardStep(ipw.VBox, awb.WizardAppWidgetStep):
    """Wizard step for running predictions with trained MLIP."""

    def __init__(self, model, **kwargs):
        """
        Initialize prediction wizard step.

        Parameters
        ----------
        model : PredictionModel
            The prediction data model
        """
        self.model = model

        self.title = ipw.HTML("<h3>Step 3: Run Predictions</h3>")
        
        self.calc_type = ipw.Dropdown(
            options=[
                ('Geometry Optimization', 'geometry_opt'),
                ('Molecular Dynamics', 'md'),
                ('Single Point', 'single_point'),
            ],
            value='geometry_opt',
            description='Calculation:',
        )
        self.calc_type.observe(self._on_calc_change, names='value')
        
        self.info = ipw.HTML(
            """
            <p>Run calculations using the trained MLIP model.</p>
            <p>Available calculation types:</p>
            <ul>
                <li><b>Geometry Optimization</b>: Find minimum energy structure</li>
                <li><b>Molecular Dynamics</b>: NVE, NVT, or NPT simulations</li>
                <li><b>Single Point</b>: Energy and forces calculation</li>
            </ul>
            """
        )
        
        self.run_button = ipw.Button(
            description='Run Calculation',
            button_style='success',
            disabled=True
        )
        self.run_button.on_click(self._on_run_click)
        
        self.status = ipw.HTML()
        self.output = ipw.Output()

        super().__init__(
            children=[
                self.title,
                self.info,
                self.calc_type,
                self.run_button,
                self.status,
                self.output
            ],
            **kwargs
        )
    
    def _on_calc_change(self, change):
        """Handle calculation type selection."""
        self.model.calculation_type = change['new']
        calc_names = {
            'geometry_opt': 'Geometry Optimization',
            'md': 'Molecular Dynamics', 
            'single_point': 'Single Point'
        }
        self.status.value = f"<p>Selected: {calc_names[change['new']]}</p>"
        self.run_button.disabled = False
    
    def _on_run_click(self, button):
        """Handle run button click."""
        with self.output:
            self.output.clear_output()
            
            if not AIIDA_MLIP_AVAILABLE:
                print("❌ aiida-mlip not available. Install with:")
                print("   pip install aiida-mlip")
                self.status.value = "<p style='color: red;'>❌ aiida-mlip not installed</p>"
                return
            
            # Get structure from Step 1 (passed via main.py observer)
            structure = getattr(self, '_parent_structure', None)
            if structure is None:
                print("❌ No structure uploaded. Please go to Step 1 and upload a structure.")
                self.status.value = "<p style='color: red;'>❌ No structure available</p>"
                return
            
            calc_type = self.model.calculation_type
            
            try:
                # Convert ASE structure to AiiDA
                print(f"Converting structure: {structure.get_chemical_formula()}")
                structure_node = orm.StructureData(ase=structure)
                
                # Load the code
                print("Loading janus code...")
                try:
                    code = orm.load_code('janus@localhost')
                except Exception:
                    print("❌ Code 'janus@localhost' not found. Setting up...")
                    print("   Run: verdi code create core.code.installed --config janus.yml")
                    self.status.value = "<p style='color: red;'>❌ Code not configured</p>"
                    return
                
                # Download and create model
                print("Loading MACE-MP-0 small model...")
                model_uri = "https://github.com/stfc/janus-core/raw/main/tests/models/mace_mp_small.model"
                model = ModelData.from_uri(model_uri, architecture="mace_mp", cache_dir="mlips")
                
                # Build calculation based on type
                if calc_type == 'geometry_opt':
                    print("Setting up Geometry Optimization...")
                    builder = GeomOpt.get_builder()
                    builder.code = code
                    builder.struct = structure_node
                    builder.model = model
                    builder.arch = orm.Str(model.architecture)
                    builder.device = orm.Str('cpu')
                    builder.fmax = orm.Float(0.05)
                    builder.steps = orm.Int(500)
                    display_name = "Geometry Optimization"
                    
                elif calc_type == 'single_point':
                    print("Setting up Single Point calculation...")
                    builder = Singlepoint.get_builder()
                    builder.code = code
                    builder.struct = structure_node
                    builder.model = model
                    builder.arch = orm.Str(model.architecture)
                    builder.device = orm.Str('cpu')
                    display_name = "Single Point"
                    
                elif calc_type == 'md':
                    print("❌ MD calculations not yet implemented")
                    self.status.value = "<p style='color: orange;'>⚠ MD coming soon</p>"
                    return
                
                # Set computation resources
                builder.metadata.options.resources = {'num_machines': 1}
                builder.metadata.options.max_wallclock_seconds = 3600
                
                # Submit calculation
                print(f"Submitting {display_name}...")
                node = engine.submit(builder)
                
                print(f"✓ Submitted successfully!")
                print(f"  PK: {node.pk}")
                print(f"  UUID: {node.uuid}")
                print(f"\nCheck status with: verdi process list")
                print(f"Or view results in Step 4 with PK: {node.pk}")
                
                self.status.value = f"<p style='color: green;'>✓ {display_name} submitted (PK: {node.pk})</p>"
                self.model.calculation_node = node
                
                # Store PK for results step (if main app model is available)
                if hasattr(self, '_app_model') and hasattr(self._app_model, 'results_model'):
                    self._app_model.results_model.calculation_pk = node.pk
                
            except Exception as e:
                print(f"❌ Error submitting calculation: {e}")
                import traceback
                traceback.print_exc()
                self.status.value = f"<p style='color: red;'>❌ Submission failed</p>"
