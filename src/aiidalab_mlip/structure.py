"""Structure selection wizard step."""

import io
import tempfile

import aiidalab_widgets_base as awb
import ipywidgets as ipw
import traitlets
from ase import Atoms
from ase.io import read as ase_read


class StructureWizardStep(ipw.VBox, awb.WizardAppWidgetStep):
    """Wizard step for structure selection."""

    def __init__(self, model, **kwargs):
        """
        Initialize structure wizard step.

        Parameters
        ----------
        model : StructureModel
            The structure data model
        """
        self.model = model

        # Title
        self.title = ipw.HTML("<h3>Step 1: Select or Upload Structure</h3>")
        
        # File upload widget
        self.upload_widget = ipw.FileUpload(
            accept='.cif,.xyz,.pdb,.POSCAR',
            multiple=False,
            description='Upload Structure'
        )
        self.upload_widget.observe(self._on_file_upload, names='value')
        
        # Structure viewer (simple output for now)
        self.structure_viewer = ipw.Output()
        
        # Status message
        self.status = ipw.HTML()
        
        self.info = ipw.HTML(
            """
            <p>Upload a structure file (CIF, XYZ, PDB, or POSCAR format).</p>
            <p>Supported formats: CIF, XYZ, PDB, VASP POSCAR</p>
            """
        )

        super().__init__(
            children=[self.title, self.info, self.upload_widget, 
                     self.status, self.structure_viewer],
            **kwargs
        )
    
    def _on_file_upload(self, change):
        """Handle file upload."""
        if not change['new']:
            return
        
        # Get uploaded file
        uploaded = change['new']
        filename = list(uploaded.keys())[0]
        content = uploaded[filename]['content']
        
        try:
            # Write to temporary file and read with ASE
            with tempfile.NamedTemporaryFile(mode='wb', suffix=filename, delete=False) as f:
                f.write(content)
                temp_path = f.name
            
            # Read structure
            structure = ase_read(temp_path)
            
            # Store in model
            self.model.structure = structure
            self.model.filename = filename
            
            # Update status
            self.status.value = f"<p style='color: green;'>Loaded {filename}: {len(structure)} atoms</p>"
            
            # Display structure info
            with self.structure_viewer:
                self.structure_viewer.clear_output()
                print(f"Formula: {structure.get_chemical_formula()}")
                print(f"Number of atoms: {len(structure)}")
                print(f"Cell: {structure.get_cell()}")
            
            # Mark step as configured
            self.state = 'SUCCESS'
            
        except Exception as e:
            self.status.value = f"<p style='color: red;'>✗ Error reading file: {str(e)}</p>"
            self.state = 'FAIL'
