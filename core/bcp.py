import cv2
import math
import numpy as np


def estimatebrightchannel(im,sz):
	b,g,r = cv2.split(im)
	bc = cv2.max(cv2.max(r,g),b)
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(sz,sz))
	bright = cv2.dilate(bc,kernel)
	return bright


def Guidedfilter(im,p,r,eps):
	mean_I = cv2.boxFilter(im,cv2.CV_64F,(r,r))
	mean_p = cv2.boxFilter(p, cv2.CV_64F,(r,r))
	mean_Ip = cv2.boxFilter(im*p,cv2.CV_64F,(r,r))
	cov_Ip = mean_Ip - mean_I*mean_p

	mean_II = cv2.boxFilter(im*im,cv2.CV_64F,(r,r))
	var_I   = mean_II - mean_I*mean_I

	a = cov_Ip/(var_I + eps)
	b = mean_p - a*mean_I

	mean_a = cv2.boxFilter(a,cv2.CV_64F,(r,r))
	mean_b = cv2.boxFilter(b,cv2.CV_64F,(r,r))

	q = mean_a*im + mean_b
	return q


def TransmissionRefine(im,et):
	gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
	gray = np.float64(gray)/255
	r = 60
	eps = 0.0001
	t = Guidedfilter(gray,et,r,eps)
	return t


def normalize_img(img):
	min_v = np.amin(img)
	max_v = np.amax(img)
	return (img-min_v)/(max_v-min_v)


def estimate_illumination(src):

	im = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)

	tmin=0.1   # minimum value for t to make J image
	w=3       # window size, which determine the corseness of prior images

	alpha=0.4  # threshold for transmission correction. range is 0.0 to 1.0. The bigger number makes darker image.
	omega=0.75 # this is for dark channel prior. change this parameter to arrange dark_t's range. 0.0 to 1.0. bigger is brighter
	p=0.1      # percentage to consider for atmosphere. 0.0 to 1.0
	eps=1e-3   # for J image

	I = np.asarray(im, dtype=np.float64) # Convert the input to an array.
	I = I[:,:,:3]/255 # stackoverflow.com/questions/44955656/how-to-convert-rgb-pil-image-to-numpy-array-with-3-channels

	Ibright_ch = estimatebrightchannel(I, w)
	bright_ch_refined = TransmissionRefine(im,Ibright_ch)
	inv_bright_ch_refined = 1 - bright_ch_refined
	inv_bright_ch_refined = normalize_img(inv_bright_ch_refined)

	return inv_bright_ch_refined