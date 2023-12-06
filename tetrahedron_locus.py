from shapes import *
from shape_creation import Tetrahedron
from display_utils import *
if __name__ == "__main__":

    cube = Tetrahedron()

    fn=3
    p=np.array([[-.4], [-.6]])

    cube.add_point_to_face((p, {'color':'black','s':40}), fn)

    radii = [.5 + np.sqrt(i)/3.3 for i in range(99)]
    i=0
    color_dic={r:color for (r, color) in zip(radii, rb_gradient(len(radii)))}
    for r, color in zip(radii, rb_gradient(len(radii))):
        i+=1
        A = Arc(p, 0, np.pi*2, r)
        plot=False
        cube.add_arc_end_to_face(A, fn, arc_info={"color":color, 'plot':plot})
    cube.add_all_cut_locus_points(point_info={'color':'black','s':2},conditional_point_info=lambda r:{'color':color_dic[r]})

    cube.plot_faces()
