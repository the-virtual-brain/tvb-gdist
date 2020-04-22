import geodesic


def test_point_3d():
    point3d = geodesic.Point3D()
    actual = point3d.distance([1, 2, 3])
    expected = 3.7416573867739413
    assert actual == expected
