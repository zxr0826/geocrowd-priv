import time
import os

import numpy as np

# import multiprocessing as mult
import sys
import logging
from KExp import KExp
from Params import Params

seedList = [2172, 7818, 1254]
#q_list = [(1.0,1.0),(5.0,5.0),(10.0,10.0),(15.0,0.2)]
q_list = [(.2, .2)]
methodList = None
exp_name = None


def data_readin():
    """Read in spatial data and initialize global variables."""
    data = np.genfromtxt(Params.dataset, unpack=True)
    Params.NDIM, Params.NDATA = data.shape[0], data.shape[1]
    Params.LOW, Params.HIGH = np.amin(data, axis=1), np.amax(data, axis=1)
    logging.debug(data.shape)
    logging.debug(Params.LOW)
    logging.debug(Params.HIGH)
    return data


#x1=-116.915680, y1=37.000293, x2=-109.050173, y2=45.543541
def queryGen(queryShape, seed, random=False, x1=-106.69617, y1=34.869024, x2=-106.149577, y2=35.019524):
    """Query generation. Each of which has at least one corner point in data populated areas.
    Due to the distribution of the spatial data set, we do not want to generate many queries in 
    the blank area. Hence the query generation function here is highly related to the Washington-NewMexico
    data we use here. x1,y1,x2,y2 are the inner boundaries of the two states respectively.
    You are encouraged to write your own query generation function depending on the dataset you use."""

    logging.debug('Generating queries...')
    np.random.seed(seed)
    querylist = []
    if random:
        x_range = np.random.uniform(0.2, 15, Params.nQuery / 2)
        y_range = np.random.uniform(0.2, 15, Params.nQuery / 2)
    else:
        x_range, y_range = queryShape[0], queryShape[1]

    point_x = np.random.uniform(Params.LOW[0], x1, Params.nQuery / 2)
    point_y = np.random.uniform(y2, Params.HIGH[1], Params.nQuery / 2)
    x_low = point_x
    x_high = point_x + x_range
    y_low = point_y - y_range
    y_high = point_y
    for i in range(int(Params.nQuery / 2)):
        querylist.append(np.array([[x_low[i], y_low[i]], [x_high[i], y_high[i]]]))

    point_x = np.random.uniform(x2, Params.HIGH[0], Params.nQuery / 2)
    point_y = np.random.uniform(Params.LOW[1], y1, Params.nQuery / 2)
    x_low = point_x - x_range
    x_high = point_x
    y_low = point_y
    y_high = point_y + y_range
    for i in range(int(Params.nQuery / 2)):
        querylist.append(np.array([[x_low[i], y_low[i]], [x_high[i], y_high[i]]]))

    return querylist


def test_quadtreeOpt(queryShape):
    global methodList, exp_name
    exp_name = 'quadtreeOpt'
    methodList = ['Quad-baseline', 'Quad-geo', 'Quad-post', 'Quad-opt']

    #    Params.maxHeight = 10
    epsList = [0.1, 0.5, 1.0]
    data = data_readin()
    res_cube_abs = np.zeros((len(epsList), len(seedList), len(methodList)))
    res_cube_rel = np.zeros((len(epsList), len(seedList), len(methodList)))

    for j in range(len(seedList)):
        queryList = queryGen(queryShape, seedList[j])
        kexp = KExp(data, queryList)
        for i in range(len(epsList)):
            for k in range(len(methodList)):
                p = Params(seedList[j])
                p.Eps = epsList[i]
                if methodList[k] == 'Quad-baseline':
                    res_cube_abs[i, j, k], res_cube_rel[i, j, k] = kexp.run_Quad_baseline(p)
                elif methodList[k] == 'Quad-geo':
                    res_cube_abs[i, j, k], res_cube_rel[i, j, k] = kexp.run_Quad_geo(p)
                elif methodList[k] == 'Quad-post':
                    res_cube_abs[i, j, k], res_cube_rel[i, j, k] = kexp.run_Quad_post(p)
                elif methodList[k] == 'Quad-opt':
                    res_cube_abs[i, j, k], res_cube_rel[i, j, k] = kexp.run_Quad_opt(p)
                else:
                    logging.error('No such index structure!')
                    sys.exit(1)

    res_abs_summary = np.average(res_cube_abs, axis=1)
    res_rel_summary = np.average(res_cube_rel, axis=1)
    np.savetxt(Params.resdir + exp_name + '_abs_' + str(int(queryShape[0] * 10)) + '_' + str(int(queryShape[1] * 10)),
               res_abs_summary, fmt='%.4f')
    np.savetxt(Params.resdir + exp_name + '_rel_' + str(int(queryShape[0] * 10)) + '_' + str(int(queryShape[1] * 10)),
               res_rel_summary, fmt='%.4f')


def test_kdTrees(queryShape):
    global methodList, exp_name
    exp_name = 'kdTrees'
    methodList = ['pure', 'true', 'standard', 'hybrid', 'cell', 'noisymean']
    #    Params.maxHeight = 8
    epsList = [0.1, 0.5, 1.0]
    data = data_readin()
    res_cube_abs = np.zeros((len(epsList), len(seedList), len(methodList)))
    res_cube_rel = np.zeros((len(epsList), len(seedList), len(methodList)))

    for j in range(len(seedList)):
        queryList = queryGen(queryShape, seedList[j])
        kexp = KExp(data, queryList)
        for i in range(len(epsList)):
            for k in range(len(methodList)):
                p = Params(seedList[j])
                p.Eps = epsList[i]
                if methodList[k] == 'pure':
                    res_cube_abs[i, j, k], res_cube_rel[i, j, k] = kexp.run_Kd_pure(p)
                elif methodList[k] == 'true':
                    res_cube_abs[i, j, k], res_cube_rel[i, j, k] = kexp.run_Kd_true(p)
                elif methodList[k] == 'standard':
                    res_cube_abs[i, j, k], res_cube_rel[i, j, k] = kexp.run_Kd_standard(p)
                elif methodList[k] == 'hybrid':
                    res_cube_abs[i, j, k], res_cube_rel[i, j, k] = kexp.run_Kd_hybrid(p)
                elif methodList[k] == 'noisymean':
                    res_cube_abs[i, j, k], res_cube_rel[i, j, k] = kexp.run_Kd_noisymean(p)
                elif methodList[k] == 'cell':
                    res_cube_abs[i, j, k], res_cube_rel[i, j, k] = kexp.run_Kd_cell(p)
                else:
                    logging.error('No such index structure!')
                    sys.exit(1)

    res_abs_summary = np.average(res_cube_abs, axis=1)
    res_rel_summary = np.average(res_cube_rel, axis=1)
    np.savetxt(Params.resdir + exp_name + '_abs_' + str(int(queryShape[0] * 10)) + '_' + str(int(queryShape[1] * 10)),
               res_abs_summary, fmt='%.4f')
    np.savetxt(Params.resdir + exp_name + '_rel_' + str(int(queryShape[0] * 10)) + '_' + str(int(queryShape[1] * 10)),
               res_rel_summary, fmt='%.4f')


def test_height(queryShape):
    heightList = [6, 7, 8, 9, 10]
    methodList = ['quad-opt', 'hybrid', 'cell', 'hilbert']
    data = data_readin()
    res_cube_abs = np.zeros((len(heightList), len(seedList), len(methodList)))
    res_cube_rel = np.zeros((len(heightList), len(seedList), len(methodList)))

    for j in range(len(seedList)):
        queryList = queryGen(queryShape, seedList[j])
        kexp = KExp(data, queryList)
        p = Params(seedList[j])
        for i in range(len(heightList)):
            Params.maxHeight = heightList[i]
            for k in range(len(methodList)):
                if methodList[k] == 'quad-opt':
                    res_cube_abs[i, j, k], res_cube_rel[i, j, k] = kexp.run_Quad_opt(p)
                elif methodList[k] == 'hybrid':
                    res_cube_abs[i, j, k], res_cube_rel[i, j, k] = kexp.run_Kd_hybrid(p)
                elif methodList[k] == 'cell':
                    res_cube_abs[i, j, k], res_cube_rel[i, j, k] = kexp.run_Kd_cell(p)
                elif methodList[k] == 'hilbert':
                    res_cube_abs[i, j, k], res_cube_rel[i, j, k] = kexp.run_Hilbert(p)
                else:
                    logging.error('No such index structure!')
                    sys.exit(1)

    res_abs_summary = np.average(res_cube_abs, axis=1)
    res_rel_summary = np.average(res_cube_rel, axis=1)
    for s in ['abs', 'rel']:
        summary = eval('res_' + s + '_summary')
        outName = Params.resdir + 'height_' + str(int(queryShape[0] * 10)) + '_' + str(int(queryShape[1] * 10)) + str
        outFile = open(outName, 'w')
        outFile.write('#; ' + '; '.join(methodList) + '\n')
        for i in range(len(heightList)):
            outFile.write(heightList[i])
            for j in range(len(methodList)):
                outFile.write(' ' + summary[i, j])
            outFile.write('\n')
        outFile.close()


def createGnuData():
    """
    Post-processing output files to generate Gnuplot-friendly outcomes
    """
    epsList = [0.1, 0.5, 1.0]
    line = 0
    for eps in epsList:
        for type in ['abs', 'rel']:
            out = open(Params.resdir + exp_name + '_eps' + str(int(eps * 10)) + '_' + type, 'w')
            out.write('#; ' + '; '.join(methodList) + '\n')
            q_num = 1
            for queryShape in q_list:
                fileName = Params.resdir + exp_name + '_' + type + '_' + str(int(queryShape[0] * 10)) + '_' + str(
                    int(queryShape[1] * 10))
                try:
                    thisfile = open(fileName, 'r')
                except:
                    sys.exit('no input result file!')
                out.write(str(q_num) + ' ' + thisfile.readlines()[line])
                thisfile.close()
                q_num += 1
            out.close()
        line += 1

    for type in ['abs', 'rel']:
        for queryShape in q_list:
            fileName = Params.resdir + exp_name + '_' + type + '_' + str(int(queryShape[0] * 10)) + '_' + str(
                int(queryShape[1] * 10))
            os.remove(fileName)


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG, filename='debug.log')
    logging.info(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + "  START")

    ### Experiment 1: test quadtree optimizations ###
    for q_shape in q_list:
        test_quadtreeOpt(q_shape)
    createGnuData()
    ### Experiment 2: test various kd-trees ###
    #    for q_shape in q_list:
    #        test_kdTrees(q_shape)
    #    createGnuData()
    ## Experiment 3: test the impact of max tree height ###
    #    for q_shape in q_list:
    #        test_height(q_shape)

    ######### run with multi-core support, number of cores should be at least len(q_list) #########    
    #    pool = mult.Pool(processes=len(q_list))
    #    pool.map(test_quadtreeOpt,q_list)
    #    pool.close()
    #    pool.join()
    #
    #    pool.map(test_kdTrees,q_list)
    #    pool.close()
    #    pool.join()

    #    pool.map(test_height,q_list)
    #    pool.close()
    #    pool.join()
    ######### 

    logging.info(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + "  END") 
