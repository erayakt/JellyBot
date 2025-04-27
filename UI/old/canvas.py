import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as MplCanvas
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from config import COLOR_BG, COLOR_PRIMARY, COLOR_SECONDARY

class OceanCubeCanvas(MplCanvas):
    """Lightweight 3‑D cube for orientation viz."""
    def __init__(self, parent=None, w=5, h=5, dpi=100):
        fig = Figure(figsize=(w, h), dpi=dpi, facecolor=COLOR_BG.name())
        self.ax = fig.add_subplot(111, projection='3d', facecolor=COLOR_BG.name())
        super().__init__(fig)
        self._build_geometry()
        self.ax.set_xticks([]); self.ax.set_yticks([]); self.ax.set_zticks([])
        self.ax.grid(False)

    def _build_geometry(self):
        self.verts = np.array([
            [-1,-1,-1],[ 1,-1,-1],[ 1, 1,-1],[-1, 1,-1],
            [-1,-1, 1],[ 1,-1, 1],[ 1, 1, 1],[-1, 1, 1]
        ])
        self.faces = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[4,7,3,0]]
        self.edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]

    def update_orientation(self, gx, gy, gz, azimuth=0):
        self.ax.cla()
        Rx = np.array([[1,0,0],[0,np.cos(gx),-np.sin(gx)],[0,np.sin(gx),np.cos(gx)]])
        Ry = np.array([[np.cos(gy),0,np.sin(gy)],[0,1,0],[-np.sin(gy),0,np.cos(gy)]])
        Rz = np.array([[np.cos(gz),-np.sin(gz),0],[np.sin(gz),np.cos(gz),0],[0,0,1]])
        R  = Rz @ Ry @ Rx
        vr = self.verts @ R.T
        face_col = (*COLOR_PRIMARY.getRgbF()[:3], 0.25)
        for f in self.faces:
            poly = Poly3DCollection([vr[f]], facecolors=[face_col], edgecolors=[COLOR_SECONDARY.name()])
            self.ax.add_collection3d(poly)
        for i,j in self.edges:
            self.ax.plot3D(*zip(vr[i], vr[j]), color=COLOR_SECONDARY.name(), lw=2)
        for vec, clr in zip(R.T, ['r','g','b']):
            self.ax.quiver(0,0,0, *(vec*1.4), arrow_length_ratio=0.15, color=clr)
        self.ax.set_xlim(-2,2); self.ax.set_ylim(-2,2); self.ax.set_zlim(-2,2)
        self.ax.view_init(elev=20, azim=azimuth)
        self.draw_idle()