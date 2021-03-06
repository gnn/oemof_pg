# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 11:08:15 2015

This is a collection of helper functions which work on there own an can be
used by various classes. If there are too many helper-functions, they will
be sorted in different modules.

All special import should be in try/except loops to avoid import errors.
"""

import logging


# get_polygon_from_nuts
hlp_fkt = 'get_polygon_from_nuts'
try:
    from shapely.wkt import loads as wkt_loads
except:
    logging.info(
        'You will not be able to use the helper function: {0}'.format(hlp_fkt))
    logging.info('Install shapely to use it.')


def get_polygons_from_table(conn, schema, table, g_col='geom', n_col='name'):
    sql = '''
        SELECT {n_col}, st_astext({g_col})
        FROM {schema}.{table};
    '''.format(
        **{'n_col': n_col, 'g_col': g_col, 'schema': schema, 'table': table})
    logging.debug(sql)
    raw_data = conn.execute(sql).fetchall()
    polygon_dc = {}
    for d in raw_data:
        polygon_dc[d[0]] = [d[0], wkt_loads(d[1])]
    return polygon_dc


def get_polygon_from_nuts(conn, nuts):
    r"""A one-line summary that does not use variable names or the
    function name.

    Several sentences providing an extended description. Refer to
    variables using back-ticks, e.g. `var`.

    Parameters
    ----------
    var1 : array_like
        Array_like means all those objects -- lists, nested lists, etc. --
        that can be converted to an array.  We can also refer to
        variables like `var1`.
    var2 : int
        The type above can either refer to an actual Python type
        (e.g. ``int``), or describe the type of the variable in more
        detail, e.g. ``(N,) ndarray`` or ``array_like``.
    Long_variable_name : {'hi', 'ho'}, optional
        Choices in brackets, default first when optional.

    Returns
    -------
    type
        Explanation of anonymous return value of type ``type``.
    describe : type
        Explanation of return value named `describe`.
    out : type
        Explanation of `out`.

    Other Parameters
    ----------------
    only_seldom_used_keywords : type
        Explanation
    common_parameters_listed_above : type
        Explanation

    Raises
    ------
    BadException
        Because you shouldn't have done that.

    See Also
    --------
    otherfunc : relationship (optional)
    newfunc : Relationship (optional), which could be fairly long, in which
              case the line wraps here.
    thirdfunc, fourthfunc, fifthfunc

    Notes
    -----
    Notes about the implementation algorithm (if needed).

    This can have multiple paragraphs.

    You may include some math:

    .. math:: X(e^{j\omega } ) = x(n)e^{ - j\omega n}

    And even use a greek symbol like :math:`omega` inline.

    References
    ----------
    Cite the relevant literature, e.g. [1]_.  You may also cite these
    references in the notes section above.

    .. [1] O. McNoleg, "The integration of GIS, remote sensing,
       expert systems and adaptive co-kriging for environmental habitat
       modelling of the Highland Haggis using object-oriented, fuzzy-logic
       and neural-network techniques," Computers & Geosciences, vol. 22,
       pp. 585-588, 1996.

    Examples
    --------
    These are written in doctest format, and should illustrate how to
    use the function.

    >>> a=[1,2,3]
    >>> print [x + 3 for x in a]
    [4, 5, 6]
    >>> print "a\n\nb"
    a
    b

    """
    # TODO@Günni
    if isinstance(nuts, str):
        nuts = [nuts, 'xyz']
    logging.debug('Getting polygon from DB')
    sql = '''
        SELECT st_astext(ST_Transform(st_union(geom), 4326))
        FROM oemof.geo_nuts_rg_2013
        WHERE nuts_id in {0};
    '''.format(tuple(nuts))
    return wkt_loads(conn.execute(sql).fetchone()[0])


def get_polygon_from_postgis(conn, schema, table, gcol='geom', union=False):
    r"""A one-line summary that does not use variable names or the
    function name.

    Several sentences providing an extended description. Refer to
    variables using back-ticks, e.g. `var`.

    Parameters
    ----------
    var1 : array_like
        Array_like means all those objects -- lists, nested lists, etc. --
        that can be converted to an array.  We can also refer to
        variables like `var1`.
    var2 : int
        The type above can either refer to an actual Python type
        (e.g. ``int``), or describe the type of the variable in more
        detail, e.g. ``(N,) ndarray`` or ``array_like``.
    Long_variable_name : {'hi', 'ho'}, optional
        Choices in brackets, default first when optional.

    Returns
    -------
    type
        Explanation of anonymous return value of type ``type``.
    describe : type
        Explanation of return value named `describe`.
    out : type
        Explanation of `out`.

    Other Parameters
    ----------------
    only_seldom_used_keywords : type
        Explanation
    common_parameters_listed_above : type
        Explanation

    Raises
    ------
    BadException
        Because you shouldn't have done that.

    See Also
    --------
    otherfunc : relationship (optional)
    newfunc : Relationship (optional), which could be fairly long, in which
              case the line wraps here.
    thirdfunc, fourthfunc, fifthfunc

    Notes
    -----
    Notes about the implementation algorithm (if needed).

    This can have multiple paragraphs.

    You may include some math:

    .. math:: X(e^{j\omega } ) = x(n)e^{ - j\omega n}

    And even use a greek symbol like :math:`omega` inline.

    References
    ----------
    Cite the relevant literature, e.g. [1]_.  You may also cite these
    references in the notes section above.

    .. [1] O. McNoleg, "The integration of GIS, remote sensing,
       expert systems and adaptive co-kriging for environmental habitat
       modelling of the Highland Haggis using object-oriented, fuzzy-logic
       and neural-network techniques," Computers & Geosciences, vol. 22,
       pp. 585-588, 1996.

    Examples
    --------
    These are written in doctest format, and should illustrate how to
    use the function.

    >>> a=[1,2,3]
    >>> print [x + 3 for x in a]
    [4, 5, 6]
    >>> print "a\n\nb"
    a
    b

    """
    # TODO@Günni
    logging.debug('Getting polygon from DB table')
    if union:
        geo_string = 'st_union({0})'.format(gcol)
    else:
        geo_string = '{0}'.format(gcol)

    sql = '''
        SELECT st_astext(ST_Transform({geo_string}, 4326))
        FROM {schema}.{table};
    '''.format(**{'geo_string': geo_string, 'schema': schema, 'table': table})
    return wkt_loads(conn.execute(sql).fetchone()[0])


def tz_from_geom(connection, geometry):
    r"""Finding the timezone of a given point or polygon geometry, assuming
    that the polygon is not crossing a border of a timezone.

    Parameters
    ----------
    connection : sqlalchemy connection object
        A valid connection to a postigs database containing the timezone table
    geometry : shapely geometry object
        A point or polygon object. The polygon should not cross a timezone.

    Returns
    -------
    string
        Timezone using the naming of the IANA time zone database
    """

    # TODO@Günni
    if geometry.geom_type in ['Polygon', 'MultiPolygon']:
        coords = geometry.centroid
    else:
        coords = geometry
    sql = """
        SELECT tzid FROM oemof_test.tz_world
        WHERE st_contains(geom, ST_PointFromText('{wkt}', 4326));
        """.format(wkt=coords.wkt)
    return connection.execute(sql).fetchone()[0]


def get_windzone(conn, geometry):
    'Find windzone from map.'
    # TODO@Günni
    if geometry.geom_type in ['Polygon', 'MultiPolygon']:
        coords = geometry.centroid
    else:
        coords = geometry
    sql = """
        SELECT zone FROM oemof_test.windzones
        WHERE st_contains(geom, ST_PointFromText('{wkt}', 4326));
        """.format(wkt=coords.wkt)
    zone = conn.execute(sql).fetchone()
    if zone is not None:
        zone = zone[0]
    else:
        zone = 0
    return zone
