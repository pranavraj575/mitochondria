import numpy as np
from scipy.spatial import Voronoi
from src.face import Face


def _adjust_bounds(ax, points):
    margin = 0.1*points.ptp(axis=0)
    xy_min = points.min(axis=0) - margin
    xy_max = points.max(axis=0) + margin
    ax.set_xlim(xy_min[0], xy_max[0])
    ax.set_ylim(xy_min[1], xy_max[1])


def voronoi_diagram_calc(points, face: Face = None):
    vor = Voronoi(points)
    if vor.points.shape[1] != 2:
        raise ValueError("Voronoi diagram is not 2-D")

    center = vor.points.mean(axis=0)

    point_pair_to_type_and_line = dict()

    for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):  # iterates through all lines
        # pointidx: two indices of points that create this line
        # simplex: two indices of vertices of the vornoi diagram that create this line
        #       if there is an infinite vertex, there is a -1 here
        simplex = np.asarray(simplex)

        if np.all(simplex >= 0):
            point_pair_to_type_and_line[tuple(pointidx)] = ('segment',
                                                            (vor.vertices[simplex[0]], vor.vertices[simplex[1]]))

        else:
            i = simplex[simplex >= 0][0]  # finite end Voronoi vertex

            t = vor.points[pointidx[1]] - vor.points[pointidx[0]]  # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[pointidx].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n))*n

            if (vor.furthest_site):
                direction = -direction
            point_pair_to_type_and_line[tuple(pointidx)] = ('ray',
                                                            (vor.vertices[i], direction)
                                                            )
    if face is not None:
        out = dict()
        for point_pair in point_pair_to_type_and_line:
            segtype, (a, b) = point_pair_to_type_and_line[point_pair]
            if segtype == 'segment':
                new_seg = face.get_segment_within_bounds(a, b)
            elif segtype == 'ray':
                new_seg = face.get_ray_within_bounds(a, b)
            else:
                raise Exception(segtype)
            if new_seg is not None:
                out[point_pair] = ('segment', new_seg)
        return out
    return point_pair_to_type_and_line


from src.utils import within_bounds, get_correct_end_points


def voronoi_plot_2d(points, ax=None, **kw):
    """
    Plot the given Voronoi diagram in 2-D

    Parameters
    ----------
    points : points to plot
    ax : matplotlib.axes.Axes instance, optional
        Axes to plot on
    show_points : bool, optional
        Add the Voronoi points to the plot.
    show_vertices : bool, optional
        Add the Voronoi vertices to the plot.
    label_lines : (point, point)->str, optional
        label lines in plot, function is point pair to the name
    line_colors : string, optional
        Specifies the line color for polygon boundaries
    line_width : float, optional
        Specifies the line width for polygon boundaries
    line_alpha : float, optional
        Specifies the line alpha for polygon boundaries
    point_size : float, optional
        Specifies the size of points

    Returns
    -------
    fig : matplotlib.figure.Figure instance
        Figure for the plot
    points_to_segments: dictionary of point index to line segments the point creates
        segments are represetned as
    """

    from matplotlib.collections import LineCollection

    vor = Voronoi(points)
    if vor.points.shape[1] != 2:
        raise ValueError("Voronoi diagram is not 2-D")

    if ax is not None:
        if kw.get('show_points', True):
            point_size = kw.get('point_size', None)
            ax.plot(vor.points[:, 0], vor.points[:, 1], '.', markersize=point_size)
        if kw.get('show_vertices', True):
            ax.plot(vor.vertices[:, 0], vor.vertices[:, 1], 'o')

    line_colors = kw.get('line_colors', 'k')
    line_width = kw.get('line_width', 1.0)
    line_alpha = kw.get('line_alpha', 1.0)
    line_label_dist = kw.get('line_label_dist', .3)
    point_names = kw.get('point_names', None)
    label_point = None

    center = vor.points.mean(axis=0)
    ptp_bound = vor.points.ptp(axis=0)

    finite_segments = []
    infinite_segments = []
    points_to_segments = {i: list() for i in
                          range(vor.npoints)}  # dictionary of point indices to the segments they create
    text_positions = []  # list of label positions so that the next one is far from the previous
    for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):  # iterates through all lines
        # pointidx: two indices of points that create this line
        # simplex: two indices of vertices of the vornoi diagram that create this line
        #       if there is an infinite vertex, there is a -1 here
        simplex = np.asarray(simplex)
        avg_point = (vor.points[pointidx[1]] + vor.points[pointidx[0]])/2
        # midpoint the two points whose bisection forms the line
        # for labeling purposes
        tangeant = vor.points[pointidx[1]] - vor.points[pointidx[0]]
        tangeant = tangeant/np.linalg.norm(tangeant)
        if np.dot((1, 1), tangeant) < 0:
            tangeant = -tangeant

        if np.all(simplex >= 0):
            finite_segments.append(vor.vertices[simplex])
            for idx in pointidx:
                points_to_segments[idx].append((vor.vertices[simplex[0]], vor.vertices[simplex[1]]))
            if ax is not None:
                a, b = get_correct_end_points(vor.vertices[simplex[0]], vor.vertices[simplex[1]], ax.get_xlim(),
                                              ax.get_ylim())
                if a is None:
                    label_point = None
                else:
                    label_point = (a + b)/2

        else:
            i = simplex[simplex >= 0][0]  # finite end Voronoi vertex

            t = vor.points[pointidx[1]] - vor.points[pointidx[0]]  # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[pointidx].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n))*n
            if (vor.furthest_site):
                direction = -direction
            far_point = vor.vertices[i] + direction*ptp_bound.max()

            infinite_segments.append([vor.vertices[i], far_point])
            for idx in pointidx:
                points_to_segments[idx].append((vor.vertices[i], far_point))
            if ax is not None:
                a, b = get_correct_end_points(vor.vertices[i], far_point, ax.get_xlim(),
                                              ax.get_ylim())
                if a is None:
                    label_point = None
                else:
                    label_point = (a + b)/2

        if ax is not None and kw.get('label_lines', False) and label_point is not None:
            # push label point off line
            potential_text_points = [
                                        label_point + tangeant*(1 + dx/10)*line_label_dist for dx in range(10)
                                    ] + [
                                        label_point - tangeant*(3 + dx/10)*line_label_dist for dx in range(10)
                                    ]
            text_point = None
            if len(text_positions) > 0:
                satisfiable = False
                for i in range(len(potential_text_points)):
                    text_point = potential_text_points[i]
                    if min(np.linalg.norm(np.array(text_positions) - text_point, axis=1)) > 1.5:
                        satisfiable = True
                        break
                if not satisfiable:
                    text_point = max(potential_text_points,
                                     key=lambda pt: min(np.linalg.norm(np.array(text_positions) - pt, axis=1)))
            else:
                text_point = potential_text_points[0]

            text_positions.append(text_point)
            label_idxes = sorted([pointidx[0], pointidx[1]])
            label_names = []
            for pt_idx in label_idxes:
                if point_names is not None and pt_idx < len(point_names):
                    label_names.append(str(point_names[pt_idx]))
                else:
                    label_names.append(str(pt_idx))
            if within_bounds(text_point):
                ax.annotate('$\\mathbf{\\ell}^{' + '\\{' + label_names[0] + ',' + label_names[1] + '\\}' + '}$',
                            (text_point[0], text_point[1]), rotation=0, color=line_colors)
                diff = (label_point - text_point)
                ax.arrow(
                    text_point[0],  # x
                    text_point[1],  # y
                    diff[0],  # dx
                    diff[1],  # dy
                    width=.03,
                    color=line_colors,
                    alpha=line_alpha,
                    length_includes_head=True,
                )

    fig = None
    if ax is not None:
        ax.add_collection(LineCollection(finite_segments,
                                         colors=line_colors,
                                         lw=line_width,
                                         alpha=line_alpha,
                                         linestyle='solid'))
        ax.add_collection(LineCollection(infinite_segments,
                                         colors=line_colors,
                                         lw=line_width,
                                         alpha=line_alpha,
                                         linestyle='solid'))

        _adjust_bounds(ax, vor.points)
        fig = ax.figure
    return fig, points_to_segments


if __name__ == '__main__':
    from src.bound import Bound

    th = lambda theta: np.array([np.cos(theta), np.sin(theta)])

    fc = Face('test', .0001)
    n = 4
    bound_len = 2
    for theta in np.arange(n)*2*np.pi/n:
        b = Bound(m=th(theta).reshape((1, -1)), b=bound_len, s=np.array([[0], [0]]),
                  T=np.array([[1, 0.], [0, 1]]), si=np.array([[0], [0]]),
                  )
        fc.add_boundary(b, None)
    # fc = None
    points = np.array([[0, 0],
                       [-1, -1],
                       [-1, 1],
                       [1, -1],
                       [1, 1],
                       ])
    points = np.array([[0, 0], ] +
                      [th(i*2*np.pi/5 + np.pi/10) for i in range(5)] +
                      [1.4*th(i*2*np.pi/5 + np.pi/5 + np.pi/10) for i in range(5)] +
                      [5*th(i*2*np.pi/5 + np.pi/5 + np.pi/10) for i in range(5)])
    import matplotlib.pyplot as plt

    plt.scatter(points[:, 0], points[:, 1])
    diag = voronoi_diagram_calc(points,
                                face=fc,
                                )
    for pair in diag:
        segtype, (a, b) = diag[pair]
        if segtype == 'segment':
            plt.plot((a[0], b[0]), (a[1], b[1]), color='black')
        elif segtype == 'ray':
            plt.arrow(a[0], a[1], b[0], b[1], color='black', head_width=.1)
    if fc is not None:
        vxs = np.zeros((len(fc.vertices) + 1, 2))
        for i, (vx, _) in enumerate(fc.vertices):
            vxs[i, :] = vx.flatten()

        vxs[-1, :] = fc.vertices[0][0].flatten()
        plt.plot(vxs[:, 0], vxs[:, 1])
    plt.show()
