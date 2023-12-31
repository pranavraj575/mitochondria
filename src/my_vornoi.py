import numpy as np

__all__ = ['voronoi_plot_2d']


def _adjust_bounds(ax, points):
    margin = 0.1*points.ptp(axis=0)
    xy_min = points.min(axis=0) - margin
    xy_max = points.max(axis=0) + margin
    ax.set_xlim(xy_min[0], xy_max[0])
    ax.set_ylim(xy_min[1], xy_max[1])


def voronoi_plot_2d(vor, ax=None, **kw):
    """
    Plot the given Voronoi diagram in 2-D

    Parameters
    ----------
    vor : scipy.spatial.Voronoi instance
        Diagram to plot
    ax : matplotlib.axes.Axes instance, optional
        Axes to plot on
    show_points : bool, optional
        Add the Voronoi points to the plot.
    show_vertices : bool, optional
        Add the Voronoi vertices to the plot.
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

    center = vor.points.mean(axis=0)
    ptp_bound = vor.points.ptp(axis=0)

    finite_segments = []
    infinite_segments = []
    points_to_segments = {i: list() for i in range(vor.npoints)}  # dictionary of point indices to the segments they create
    for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):  # iterates through all lines
        # pointidx: two indices of points that create this line
        # simplex: two indices of vertices of the vornoi diagram that create this line
        #       if there is an infinite vertex, there is a -1 here
        simplex = np.asarray(simplex)
        if np.all(simplex >= 0):
            finite_segments.append(vor.vertices[simplex])
            for idx in pointidx:
                points_to_segments[idx].append((vor.vertices[simplex[0]], vor.vertices[simplex[1]]))
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
