# Based on <https://docs.pytest.org/en/latest/example/parametrize.html#a-quick-port-of-testscenarios>
def pytest_generate_tests(metafunc):
    idlist = []
    argvalues = []
    for scenario in metafunc.module.scenarios:
        idlist.append(scenario[0])
        argvalues.append([scenario[1][argname] for argname in metafunc.fixturenames])
    metafunc.parametrize(metafunc.fixturenames, argvalues, ids=idlist, scope="module")
