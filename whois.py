#!/usr/bin/env python

# Copyright (C) 2004, 2005 by FKtPp, baa
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#


from moobot_module import MooBotModule
""" whois.py - whois module for moobot"""
handler_list = ["whois"]

class whois(MooBotModule):
	branchServer = "whois.arin.net"

	def __init__(self):
		# init regex
		import re

		num0_255 = '(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
		ipv4part = '(?:%s\.|%s(?:\.%s){1,3})' % (num0_255, num0_255, num0_255)
		self.pIpv4Part = re.compile('^%s$' % (ipv4part))
		fields = ["inetnum",
				  "netname",
				  "country",
				  "descr",
				  "Domain Name",
				  "Registrar",
				  "Expiration Date"]
		self.pdata = re.compile('^(\s*(%s):.*)' % "|".join(fields), re.I | re.M)
		self.preferral = re.compile('^ReferralServer:\s+(?:whois://)?([^:\r\n]+)(?::(\d+))?', re.I | re.M)

		# handler regex
		self.regex = '^(?:(?:whois|whios)\s+.+|%s)$' % (ipv4part)
		self.priority = 4

		# list from GNU whois
		# {{{ IPv4
		ipv4_list = (("24.132.0.0", 14, "ripe"),\
						  ("58.0.0.0", 7, "apnic"),\
						  ("61.72.0.0", 13, "whois.nic.or.kr"),\
						  ("61.80.0.0", 14, "whois.nic.or.kr"),\
						  ("61.84.0.0", 15, "whois.nic.or.kr"),\
						  ("61.112.0.0", 12, "whois.nic.ad.jp"),\
						  ("61.192.0.0", 12, "whois.nic.ad.jp"),\
						  ("61.208.0.0", 13, "whois.nic.ad.jp"),\
						  ("60.0.0.0", 7, "apnic"),\
						  ("62.0.0.0", 8, "ripe"),\
						  ("80.0.0.0", 5, "ripe"),\
						  ("88.0.0.0", 8, "ripe"),\
						  ("96.0.0.0", 3, "UNALLOCATED"),\
						  ("0.0.0.0", 1, "arin"),\
						  ("133.0.0.0", 8, "whois.nic.ad.jp"),\
						  ("139.20.0.0", 14, "ripe"),\
						  ("139.24.0.0", 14, "ripe"),\
						  ("139.28.0.0", 15, "ripe"),\
						  ("141.0.0.0", 10, "ripe"),\
						  ("141.64.0.0", 12, "ripe"),\
						  ("141.80.0.0", 14, "ripe"),\
						  ("141.84.0.0", 15, "ripe"),\
						  ("145.0.0.0", 8, "ripe"),\
						  ("146.48.0.0", 16, "ripe"),\
						  ("149.202.0.0", 15, "ripe"),\
						  ("149.204.0.0", 16, "ripe"),\
						  ("149.206.0.0", 15, "ripe"),\
						  ("149.208.0.0", 12, "ripe"),\
						  ("149.224.0.0", 12, "ripe"),\
						  ("149.240.0.0", 13, "ripe"),\
						  ("149.248.0.0", 14, "ripe"),\
						  ("150.183.0.0", 16, "whois.nic.or.kr"),\
						  ("150.254.0.0", 16, "ripe"),\
						  ("151.0.0.0", 10, "ripe"),\
						  ("151.64.0.0", 11, "ripe"),\
						  ("151.96.0.0", 14, "ripe"),\
						  ("151.100.0.0", 16, "ripe"),\
						  ("160.216.0.0", 14, "ripe"),\
						  ("160.220.0.0", 16, "ripe"),\
						  ("160.44.0.0", 14, "ripe"),\
						  ("160.48.0.0", 12, "ripe"),\
						  ("163.156.0.0", 14, "ripe"),\
						  ("163.160.0.0", 12, "ripe"),\
						  ("164.0.0.0", 11, "ripe"),\
						  ("164.32.0.0", 13, "ripe"),\
						  ("164.40.0.0", 16, "ripe"),\
						  ("164.128.0.0", 12, "ripe"),\
						  ("169.208.0.0", 12, "apnic"),\
						  ("171.16.0.0", 12, "ripe"),\
						  ("171.32.0.0", 15, "ripe"),\
						  ("188.0.0.0", 8, "ripe "),\
						  ("128.0.0.0", 2, "arin"),\
						  ("192.71.0.0", 16, "ripe"),\
						  ("192.72.0.0", 16, "whois.seed.net.tw"),\
						  ("192.106.0.0", 16, "ripe"),\
						  ("192.114.0.0", 15, "ripe"),\
						  ("192.116.0.0", 15, "ripe"),\
						  ("192.118.0.0", 16, "ripe"),\
						  ("192.162.0.0", 16, "ripe"),\
						  ("192.164.0.0", 14, "ripe"),\
						  ("192.0.0.0", 8, "arin"),\
						  ("193.0.0.0", 8, "ripe"),\
						  ("194.0.0.0", 7, "ripe"),\
						  ("198.17.117.0", 24, "ripe"),\
						  ("196.200.0.0", 13, "ripe"),\
						  ("196.0.0.0", 6, "arin"),\
						  ("200.17.0.0", 16, "whois.nic.br"),\
						  ("200.18.0.0", 15, "whois.nic.br"),\
						  ("200.20.0.0", 16, "whois.nic.br"),\
						  ("200.96.0.0", 13, "whois.nic.br"),\
						  ("200.128.0.0", 9, "whois.nic.br"),\
						  ("200.0.0.0", 7, "lacnic"),\
						  ("202.11.0.0", 16, "whois.nic.ad.jp"),\
						  ("202.13.0.0", 16, "whois.nic.ad.jp"),\
						  ("202.15.0.0", 16, "whois.nic.ad.jp"),\
						  ("202.16.0.0", 14, "whois.nic.ad.jp"),\
						  ("202.20.128.0", 17, "whois.nic.or.kr"),\
						  ("202.23.0.0", 16, "whois.nic.ad.jp"),\
						  ("202.24.0.0", 15, "whois.nic.ad.jp"),\
						  ("202.26.0.0", 16, "whois.nic.ad.jp"),\
						  ("202.30.0.0", 15, "whois.nic.or.kr"),\
						  ("202.32.0.0", 14, "whois.nic.ad.jp"),\
						  ("202.48.0.0", 16, "whois.nic.ad.jp"),\
						  ("202.39.128.0", 17, "twnic"),\
						  ("202.208.0.0", 12, "whois.nic.ad.jp"),\
						  ("202.224.0.0", 11, "whois.nic.ad.jp "),\
						  ("203.0.0.0", 10, "apnic"),\
						  ("203.66.0.0", 16, "twnic"),\
						  ("203.69.0.0", 16, "twnic"),\
						  ("203.74.0.0", 15, "twnic"),\
						  ("203.136.0.0", 14, "whois.nic.ad.jp"),\
						  ("203.140.0.0", 15, "whois.nic.ad.jp"),\
						  ("203.178.0.0", 15, "whois.nic.ad.jp"),\
						  ("203.180.0.0", 14, "whois.nic.ad.jp"),\
						  ("203.224.0.0", 11, "whois.nic.or.kr "),\
						  ("202.0.0.0", 7, "apnic"),\
						  ("204.0.0.0", 14, "verio"),\
						  ("204.0.0.0", 6, "arin"),\
						  ("208.0.0.0", 7, "arin"),\
						  ("209.94.192.0", 19, "lacnic"),\
						  ("210.59.128.0", 17, "twnic"),\
						  ("210.61.0.0", 16, "twnic"),\
						  ("210.62.252.0", 22, "twnic"),\
						  ("210.65.0.0", 16, "twnic"),\
						  ("210.71.128.0", 16, "twnic"),\
						  ("210.90.0.0", 15, "whois.nic.or.kr"),\
						  ("210.92.0.0", 14, "whois.nic.or.kr"),\
						  ("210.96.0.0", 11, "whois.nic.or.kr "),\
						  ("210.128.0.0", 11, "whois.nic.ad.jp"),\
						  ("210.160.0.0", 12, "whois.nic.ad.jp"),\
						  ("210.178.0.0", 15, "whois.nic.or.kr"),\
						  ("210.180.0.0", 14, "whois.nic.or.kr"),\
						  ("210.188.0.0", 14, "whois.nic.ad.jp"),\
						  ("210.196.0.0", 14, "whois.nic.ad.jp"),\
						  ("210.204.0.0", 14, "whois.nic.or.kr"),\
						  ("210.216.0.0", 13, "whois.nic.or.kr"),\
						  ("210.224.0.0", 12, "whois.nic.ad.jp"),\
						  ("210.240.0.0", 16, "twnic"),\
						  ("210.241.0.0", 15, "twnic"),\
						  ("210.241.224.0", 19, "twnic"),\
						  ("210.242.0.0", 15, "twnic"),\
						  ("210.248.0.0", 13, "whois.nic.ad.jp"),\
						  ("211.0.0.0", 12, "whois.nic.ad.jp"),\
						  ("211.16.0.0", 14, "whois.nic.ad.jp"),\
						  ("211.20.0.0", 15, "twnic"),\
						  ("211.22.0.0", 16, "twnic"),\
						  ("211.32.0.0", 11, "whois.nic.or.kr"),\
						  ("211.75.0.0", 16, "twnic"),\
						  ("211.72.0.0", 16, "twnic"),\
						  ("211.104.0.0", 13, "whois.nic.or.kr"),\
						  ("211.112.0.0", 13, "whois.nic.or.kr"),\
						  ("211.120.0.0", 13, "whois.nic.ad.jp"),\
						  ("211.128.0.0", 13, "whois.nic.ad.jp"),\
						  ("211.168.0.0", 13, "whois.nic.or.kr"),\
						  ("211.176.0.0", 12, "whois.nic.or.kr"),\
						  ("211.192.0.0", 10, "whois.nic.or.kr "),\
						  ("210.0.0.0", 7, "apnic"),\
						  ("212.0.0.0", 7, "ripe"),\
						  ("214.0.0.0", 7, "arin"),\
						  ("216.0.0.0", 8, "arin"),\
						  ("217.0.0.0", 8, "ripe"),\
						  ("218.36.0.0", 14, "whois.nic.or.kr"),\
						  ("218.40.0.0", 13, "whois.nic.ad.jp"),\
						  ("218.48.0.0", 13, "whois.nic.or.kr"),\
						  ("218.144.0.0", 12, "whois.nic.or.kr"),\
						  ("218.232.0.0", 13, "whois.nic.or.kr"),\
						  ("219.240.0.0", 15, "whois.nic.or.kr"),\
						  ("219.248.0.0", 13, "whois.nic.or.kr"),\
						  ("218.0.0.0", 7, "apnic"),\
						  ("220.64.0.0", 11, "whois.nic.or.kr"),\
						  ("220.96.0.0", 14, "whois.nic.ad.jp"),\
						  ("220.103.0.0", 16, "whois.nic.or.kr"),\
						  ("220.104.0.0", 13, "whois.nic.ad.jp"),\
						  ("220.149.0.0", 16, "whois.nic.or.kr"),\
						  ("221.138.0.0", 13, "whois.nic.or.kr"),\
						  ("221.144.0.0", 12, "whois.nic.or.kr"),\
						  ("221.160.0.0", 13, "whois.nic.or.kr"),\
						  ("222.96.0.0", 12, "whois.nic.or.kr"),\
						  ("222.112.0.0", 13, "whois.nic.or.kr"),\
						  ("222.120.0.0", 15, "whois.nic.or.kr"),\
						  ("222.122.0.0", 16, "whois.nic.or.kr"),\
						  ("222.232.0.0", 13, "whois.nic.or.kr"),\
						  ("223.0.0.0", 8, "UNALLOCATED"),\
						  ("220.0.0.0", 6, "apnic"),\
						  ("0.0.0.0", 0, "DEFAULT"))
		# }}}
		# init ipv4_list
		self.ipv4_list = []
		for t_ip, t_mask, t_host in ipv4_list:
			ip = self.ipv4_atoint(t_ip)
			mask = ~((1 << (32 - t_mask)) - 1)
			self.ipv4_list.append((ip, mask, t_host))
		# {{{ TLD <== top level domain
		self.tld_list = ((".br.com", "whois.centralnic.net"),\
						 (".cn.com", "whois.centralnic.net"),\
						 (".de.com", "whois.centralnic.net"),\
						 (".eu.com", "whois.centralnic.net"),\
						 (".gb.com", "whois.centralnic.net"),\
						 (".gb.net", "whois.centralnic.net"),\
						 (".hu.com", "whois.centralnic.net"),\
						 (".no.com", "whois.centralnic.net"),\
						 (".qc.com", "whois.centralnic.net"),\
						 (".ru.com", "whois.centralnic.net"),\
						 (".sa.com", "whois.centralnic.net"),\
						 (".se.com", "whois.centralnic.net"),\
						 (".se.net", "whois.centralnic.net"),\
						 (".uk.com", "whois.centralnic.net"),\
						 (".uk.net", "whois.centralnic.net"),\
						 (".us.com", "whois.centralnic.net"),\
						 (".uy.com", "whois.centralnic.net"),\
						 (".za.com", "whois.centralnic.net"),\
						 (".eu.org", "whois.eu.org"),\
						 (".com", "CRSNIC"),\
						 (".net", "CRSNIC"),\
						 (".org", "PIR"),\
						 (".edu", "whois.educause.net"),\
						 (".gov", "whois.nic.gov"),\
						 (".int", "whois.iana.org"),\
						 (".mil", "whois.nic.mil"),\
						 (".aero", "whois.information.aero"),\
						 (".arpa", "whois.iana.org"),\
						 (".biz", "whois.nic.biz"),\
						 (".coop", "whois.nic.coop"),\
						 (".info", "whois.afilias.info"),\
						 (".museum", "whois.museum"),\
						 (".name", "whois.nic.name"),\
						 (".pro", "whois.registrypro.pro"),\
						 (".ac", "whois.nic.ac"),\
						 (".ad", "NONE"),\
						 (".ae", "whois.uaenic.ae"),\
						 (".af", "NONE"),\
						 (".ag", "whois.nic.ag"),\
						 (".ai", "WEB http://whois.offshore.ai/"),\
						 (".al", "NONE"),\
						 (".am", "whois.amnic.net"),\
						 (".am", "WEB https://www.amnic.net/whois/"),\
						 (".an", "NONE"),\
						 (".ao", "NONE"),\
						 (".aq", "NONE"),\
						 (".ar", "WEB http://www.nic.ar/consultas/consdom.html"),\
						 (".as", "whois.nic.as"),\
						 (".at", "whois.nic.at"),\
						 (".au", "whois.ausregistry.net.au"),\
						 (".az", "WEB http://www.nic.az/AzCheck.htm"),\
						 (".ba", "WEB http://www.nic.ba/stream/whois/"),\
						 (".bb", "WEB http://domains.org.bb/regsearch/"),\
						 (".bd", "NONE"),\
						 (".be", "whois.dns.be"),\
						 (".bf", "NONE"),\
						 (".bg", "whois.ripe.net"),\
						 (".bi", "WEB http://www.nic.bi/Nic_search.asp"),\
						 (".bm", "WEB http://207.228.133.14/cgi-bin/lansaweb?procfun+BMWHO+BMWHO2+WHO"),\
						 (".bo", "WEB http://www.nic.bo/"),\
						 (".br", "whois.nic.br"),\
						 (".bs", "WEB http://www.nic.bs/cgi-bin/search.pl"),\
						 (".bt", "WEB http://www.nic.bt/"),\
						 (".bv", "NONE"),\
						 (".by", "WEB http://www.tld.by/indexeng.html"),\
						 (".bz", "whois.belizenic.bz"),\
						 (".ca", "whois.cira.ca"),\
						 (".cc", "NICCC"),\
						 (".cd", "whois.nic.cd"),\
						 (".cf", "WEB http://www.nic.cf/whois.php3"),\
						 (".cg", "WEB http://www.nic.cg/cgi-bin/whoiscg.pl"),\
						 (".ch", "whois.nic.ch"),\
						 (".ci", "www.nic.ci"),\
						 (".ck", "whois.nic.ck"),\
						 (".cl", "whois.nic.cl"),\
						 (".cm", "NONE"),\
						 (".edu.cn", "whois.edu.cn"),\
						 (".cn", "whois.cnnic.net.cn"),\
						 (".uk.co", "whois.uk.co"),\
						 (".co", "WEB https://www.nic.co/"),\
						 (".cr", "WEB http://www.nic.cr/servlet/niccr?tid=TWhois&Lng=5&Act=NEW"),\
						 (".cu", "WEB http://www.nic.cu/consult.html"),\
						 (".cv", "NONE"),\
						 (".cx", "whois.nic.cx"),\
						 (".cy", "WEB http://www.nic.cy/nslookup/online_database.php"),\
						 (".cz", "whois.nic.cz"),\
						 (".de", "whois.denic.de"),\
						 (".dj", "whois.domain.dj"),\
						 (".dk", "whois.dk-hostmaster.dk"),\
						 (".dm", "NONE"),\
						 (".do", "WEB http://www.nic.do/whois-h.php3"),\
						 (".dz", "WEB http://www.nic.dz/anglais/dom-attr-eng.htm"),\
						 (".ec", "WEB http://www.nic.ec/consulta/whois.asp"),\
						 (".ee", "whois.eenet.ee"),\
						 (".eg", "NONE"),\
						 (".er", "NONE"),\
						 (".es", "WEB https://www.nic.es/esnic/jsp/whois_ctos.jsp"),\
						 (".fi", "whois.ficora.fi"),\
						 (".fj", "whois.usp.ac.fj"),\
						 (".fk", "NONE"),\
						 (".fm", "WEB http://www.dot.fm/whois.html"),\
						 (".fo", "whois.ripe.net"),\
						 (".fr", "whois.nic.fr"),\
						 (".gb", "NONE"),\
						 (".ge", "WEB http://whois.sanet.ge/"),\
						 (".gf", "whois.nplus.gf"),\
						 (".gg", "whois.channelisles.net"),\
						 (".gh", "NONE"),\
						 (".gi", "WEB http://whois.gibnet.gi/"),\
						 (".gl", "NONE"),\
						 (".gm", "whois.ripe.net"),\
						 (".gn", "NONE"),\
						 (".gr", "WEB https://grweb.ics.forth.gr/Whois?lang=en"),\
						 (".gs", "whois.adamsnames.tc"),\
						 (".gt", "WEB http://www.gt/whois.htm"),\
						 (".gu", "WEB http://gadao.gov.gu/Scripts/wwsquery/wwsquery.dll?hois=guamquery"),\
						 (".hk", "whois.hkdnr.net.hk"),\
						 (".hm", "whois.registry.hm"),\
						 (".hn", "NONE"),\
						 (".hr", "WEB http://www.dns.hr/pretrazivanje.html"),\
						 (".ht", "NONE"),\
						 (".hu", "whois.nic.hu"),\
						 (".id", "whois.idnic.net.id"),\
						 (".ie", "whois.domainregistry.ie"),\
						 (".il", "whois.isoc.org.il"),\
						 (".im", "WEB http://www.nic.im/exist.html"),\
						 (".in", "whois.ncst.ernet.in"),\
						 (".io", "whois.nic.io"),\
						 (".ir", "whois.nic.ir"),\
						 (".is", "whois.isnet.is"),\
						 (".it", "whois.nic.it"),\
						 (".je", "whois.channelisles.net"),\
						 (".jo", "WEB http://www.nis.jo/dns/"),\
						 (".jp", "whois.nic.ad.jp"),\
						 (".ke", "whois.kenic.or.ke"),\
						 (".kg", "whois.domain.kg"),\
						 (".kh", "NONE"),\
						 (".ki", "WEB http://www.ki/dns/"),\
						 (".km", "NONE"),\
						 (".kr", "whois.nic.or.kr"),\
						 (".kw", "WEB http://www.domainname.net.kw"),\
						 (".ky", "WEB http://146.115.157.215/whoisfrontend.asp"),\
						 (".kz", "whois.domain.kz"),\
						 (".la", "whois.nic.la"),\
						 (".lb", "WEB http://www.aub.edu.lb/lbdr/search.html"),\
						 (".lc", "NONE"),\
						 (".li", "whois.nic.li"),\
						 (".lk", "whois.nic.lk"),\
						 (".lr", "NONE"),\
						 (".ls", "NONE"),\
						 (".lt", "whois.ripe.net"),\
						 (".lu", "whois.dns.lu"),\
						 (".lv", "whois.nic.lv"),\
						 (".ly", "WEB http://www.lydomains.com/"),\
						 (".mc", "whois.ripe.net"),\
						 (".md", "WEB http://www.dns.md/whois.html"),\
						 (".mg", "NONE"),\
						 (".mh", "NONE"),\
						 (".mm", "whois.nic.mm"),\
						 (".mn", "whois.nic.mn"),\
						 (".mo", "NONE"),\
						 (".mp", "NONE"),\
						 (".mr", "NONE"),\
						 (".ms", "whois.adamsnames.tc"),\
						 (".mt", "WEB http://www.nic.org.mt/dir/home.html"),\
						 (".mu", "WEB http://www.nic.mu/mauritius/domain.whois.php"),\
						 (".mw", "WEB http://www.registrar.mw/"),\
						 (".mx", "whois.nic.mx"),\
						 (".my", "whois.mynic.net.my"),\
						 (".na", "whois.na-nic.com.na"),\
						 (".nc", "whois.cctld.nc"),\
						 (".nf", "WEB http://whois.nic.nf/whois.jsp"),\
						 (".ng", "NONE"),\
						 (".ni", "NONE"),\
						 (".nl", "whois.domain-registry.nl"),\
						 (".no", "whois.norid.no"),\
						 (".np", "WEB http://www.mos.com.np/domsearch.html"),\
						 (".nr", "WEB http://www.cenpac.net.nr/dns/whois.html"),\
						 (".nu", "whois.nic.nu"),\
						 (".nz", "whois.srs.net.nz"),\
						 (".pa", "WEB http://www.nic.pa/"),\
						 (".pe", "whois.nic.pe"),\
						 (".pg", "NONE"),\
						 (".ph", "WEB http://www.domains.ph/DomainSearch.asp"),\
						 (".pk", "WEB http://www.pknic.net.pk/"),\
						 (".pl", "whois.dns.pl"),\
						 (".pm", "whois.nic.fr"),\
						 (".pn", "WEB http://www.pitcairn.pn/PnRegistry/CheckAvailability.html"),\
						 (".pr", "WEB http://www.nic.pr/domain/whois.asp"),\
						 (".ps", "WEB http://www.nic.ps/whois/"),\
						 (".pt", "whois.dns.pt"),\
						 (".pw", "whois.nic.pw"),\
						 (".py", "WEB http://www.nic.py/consultas/"),\
						 (".qa", "NONE"),\
						 (".re", "whois.nic.fr"),\
						 (".ro", "whois.rotld.ro"),\
						 (".edu.ru", "whois.informika.ru"),\
						 (".ru", "whois.ripn.net"),\
						 (".rw", "WEB http://www.nic.rw/cgi-bin/whoisrw.pl"),\
						 (".sa", "saudinic.net.sa"),\
						 (".sb", "WEB http://www.nic.net.sb/search.htm"),\
						 (".sc", "NONE"),\
						 (".sd", "NONE"),\
						 (".se", "whois.nic-se.se"),\
						 (".sg", "whois.nic.net.sg"),\
						 (".sh", "whois.nic.sh"),\
						 (".si", "whois.arnes.si"),\
						 (".sj", "NONE"),\
						 (".sk", "whois.ripe.net"),\
						 (".sm", "whois.ripe.net"),\
						 (".sn", "NONE"),\
						 (".so", "NONE"),\
						 (".sr", "whois.register.sr"),\
						 (".st", "whois.nic.st"),\
						 (".su", "whois.ripn.net"),\
						 (".sv", "WEB http://www.uca.edu.sv/dns/"),\
						 (".sz", "NONE"),\
						 (".tc", "whois.adamsnames.tc"),\
						 (".td", "WEB http://www.nic.td/"),\
						 (".tf", "whois.nic.tf"),\
						 (".tg", "WEB http://www.nic.tg/"),\
						 (".th", "whois.thnic.net"),\
						 (".tj", "whois.nic.tj"),\
						 (".tk", "whois.dot.tk"),\
						 (".tm", "whois.nic.tm"),\
						 (".tn", "NONE"),\
						 (".to", "whois.tonic.to"),\
						 (".tp", "WEB http://cgi.connect.ie/cgi-bin/tplookup.cgi"),\
						 (".tr", "whois.metu.edu.tr"),\
						 (".tt", "WEB http://www.nic.tt/cgi-bin/search.pl"),\
						 (".tv", "whois.tv"),\
						 (".tw", "whois.twnic.net"),\
						 (".tz", "NONE"),\
						 (".ua", "whois.net.ua"),\
						 (".ug", "WEB http://www.registry.co.ug/whois/"),\
						 (".gov.uk", "whois.ja.net"),\
						 (".ac.uk", "whois.ja.net"),\
						 (".uk", "whois.nic.uk"),\
						 (".um", "NONE"),\
						 (".fed.us", "whois.nic.gov"),\
						 (".us", "whois.nic.us"),\
						 (".com.uy", "WEB http://dns.antel.net.uy/clientes/consultar.htm"),\
						 (".uy", "WEB http://www.rau.edu.uy/rau/dom/"),\
						 (".uz", "WEB http://www.noc.uz/dom_01.htm"),\
						 (".va", "whois.ripe.net"),\
						 (".vc", "whois.opensrs.net"),\
						 (".ve", "WEB http://www.nic.ve/nicwho01.html"),\
						 (".vg", "whois.adamsnames.tc"),\
						 (".vi", "WEB http://www.nic.vi/whoisform.htm"),\
						 (".vn", "WEB http://www.vnnic.net.vn/english/reg_domain/"),\
						 (".vu", "WEB http://www.vunic.vu/whois.htm"),\
						 (".ws", "whois.samoanic.ws"),\
						 (".yu", "NONE"),\
						 (".ac.za", "whois.ac.za"),\
						 (".co.za", "WEB http://whois.co.za/"),\
						 (".net.za", "whois.net.za"),\
						 (".org.za", "WEB http://www.org.za/"),\
						 (".za", "NONE"),\
						 (".zm", "NONE"),\
						 ("-dom", "whois.networksolutions.com"),\
						 ("-org", "whois.networksolutions.com"),\
						 ("-hst", "whois.networksolutions.com"),\
						 ("-arin", "whois.arin.net"),\
						 ("-ripe", "whois.ripe.net"),\
						 ("-mnt", "whois.ripe.net"),\
						 ("-lacnic", "whois.lacnic.net"),\
						 ("-gandi", "whois.gandi.net"),\
						 ("-ap", "whois.apnic.net"),\
						 ("-ar", "whois.aunic.net"),\
						 ("-cn", "whois.cnnic.net.cn"),\
						 ("-dk", "whois.dk-hostmaster.dk"),\
						 ("-ti", "whois.telstra.net"),\
						 ("-is", "whois.isnet.is"),\
						 ("-6bone", "whois.6bone.net"),\
						 ("-norid", "whois.norid.no"),\
						 ("-ripn", "whois.ripn.net"),\
						 ("-sgnic", "whois.nic.net.sg"),\
						 ("-metu", "whois.metu.edu.tr"),\
						 ("-cknic", "whois.nic.ck"),\
						 ("-cz", "whois.nic.cz"),\
						 ("-kg", "whois.domain.kg"),\
						 ("-rotld", "whois.rotld.ro"),\
						 ("-itnic", "whois.nic.it"),\
						 ("-frnic", "whois.nic.fr"),\
						 ("-nicat", "whois.nic.at"),\
						 ("-il", "whois.isoc.org.il"),\
						 ("-lrms", "whois.afilias.net"),\
						 ("-tw", "whois.twnic.net"),\
						 ("-nicir", "whois.nic.ir"),\
						 ("-uanic", "whois.com.ua"),\
						 ("", "DEFAULT"))
		# }}}
		# {{{ IPv6 assign
		ipv6_assign = (
				[ 0x0200, "whois.apnic.net" ],
				[ 0x0400, "whois.arin.net" ],
				[ 0x0600, "whois.ripe.net" ],
				[ 0x0800, "whois.ripe.net" ],
				[ 0x0A00, "whois.ripe.net" ],
				[ 0x0C00, "whois.apnic.net" ],
				[ 0x0E00, "whois.apnic.net" ],
				[ 0x1200, "whois.lacnic.net" ],
				[ 0x1400, "whois.ripe.net" ],
				[ 0x1600, "whois.ripe.net" ],
				[ 0x1800, "whois.arin.net" ])
		# }}}
		# init ipv6_assign
		self.ipv6_assign = {}
		for t_net, t_host in ipv6_assign:
			self.ipv6_assign[t_net] = t_host
		# {{{ IPv6
		self.as_assign = (
				[ 379, 508, "whois.nic.mil" ],
				[ 1101, 1200, "whois.ripe.net" ],
				[ 1877, 1901, "whois.ripe.net" ],
				[ 2043, 2043, "whois.ripe.net" ],
				[ 2047, 2047, "whois.ripe.net" ],
				[ 2057, 2136, "whois.ripe.net" ],
				[ 2387, 2488, "whois.ripe.net" ],
				[ 2497, 2528, "whois.nic.ad.jp" ],
				[ 2585, 2614, "whois.ripe.net" ],
				[ 2773, 2822, "whois.ripe.net" ],
				[ 2830, 2879, "whois.ripe.net" ],
				[ 3154, 3353, "whois.ripe.net" ],
				[ 4608, 4863, "whois.apnic.net" ],
				[ 5120, 5376, "whois.nic.mil" ],
				[ 5377, 5631, "whois.ripe.net" ],
				[ 5800, 6055, "whois.nic.mil" ],
				[ 6656, 6911, "whois.ripe.net" ],
				[ 7467, 7722, "whois.apnic.net" ],
				[ 8192, 9215, "whois.ripe.net" ],
				[ 9591, 9622, "whois.nic.ad.jp" ],
				[ 9628, 9647, "whois.nic.or.kr" ],
				[ 9683, 9712, "whois.nic.or.kr" ],
				[ 9753, 9784, "whois.nic.or.kr" ],
				[ 9840, 9871, "whois.nic.or.kr" ],
				[ 9943, 9982, "whois.nic.or.kr" ],
				[ 9990, 10021, "whois.nic.ad.jp" ],
				[ 9261, 10067, "whois.apnic.net" ],
				[ 10034, 10073, "whois.nic.or.kr" ],
				[ 10154, 10198, "whois.nic.or.kr" ],
				[ 10074, 10239, "whois.apnic.net" ],
				[ 12288, 13311, "whois.ripe.net" ],
				[ 15360, 16383, "whois.ripe.net" ],
				[ 17503, 17534, "whois.nic.ad.jp" ],
				[ 17567, 17616, "whois.nic.or.kr" ],
				[ 17673, 17704, "whois.nic.ad.jp" ],
				[ 17832, 17880, "whois.nic.or.kr" ],
				[ 17408, 18431, "whois.apnic.net" ],
				[ 17930, 17961, "whois.nic.ad.jp" ],
				[ 18067, 18098, "whois.nic.ad.jp" ],
				[ 18121, 18152, "whois.nic.ad.jp" ],
				[ 18259, 18290, "whois.nic.ad.jp" ],
				[ 18259, 18290, "whois.nic.ad.jp" ],
				[ 20480, 21503, "whois.ripe.net" ],
				[ 23552, 24575, "whois.apnic.net" ],
				[ 23612, 23643, "whois.nic.ad.jp" ],
				[ 24576, 25599, "whois.ripe.net" ],
				[ 26592, 26623, "whois.lacnic.net" ],
				[ 27648, 28671, "whois.lacnic.net" ],
				[ 28672, 29695, "whois.ripe.net" ],
				[ 0, 30719, "whois.arin.net" ],
				[ 0, 0, "." ])
		# }}}

	def handler(self, **args):
		"""TODO. only query from Asia Pacific Network Infomation Center, need fix"""
		query_str = args["text"].split()
		if query_str[1] in ["whois", "whios"]:
			query_str = query_str[2].strip()
		else:
			query_str = query_str[1]
		result = self.query(query_str)

		from irclib import Event
		target = self.return_to_sender(args)
		result = Event("privmsg", "", target, [ result ])
		return result

	# to machine byte order?
	def ipv4_atoint(self, str_ip):
		l = len(str_ip)
		i = 0
		j = 24
		int_ip = 0
		for part in str_ip.split("."):
			if len(part):
				int_ip += int(part) << j
				j -= 8
		return int_ip

	def decideServer(self, query_str, ipver):
		"""
		Return the most suitable server domain or ipaddress acroding the QUERY_STR
		"""
		if ipver == 4:
			IntIP = self.ipv4_atoint(query_str)
			for ip, mask, t_host in self.ipv4_list:
				if ip & mask == IntIP & mask:
					break
		elif ipver == 6:
			if query_str[0:5] == "2001:":
				v6net = int(query_str[5:].split(':')[0], 16) & 0xfe00;
				if self.ipv6_assign.has_key(v6net):
					t_host = self.ipv6_assign[v6net]
			elif query_str[0:5].lower() == "3ffe:":
				t_host = "whois.6bone.net"
		elif ipver == 0:
			query_str = query_str.lower()
			query_str_l = len(query_str)
			for tld, t_host in self.tld_list:
				if query_str[query_str_l - len(tld):] == tld:
					return (t_host, False)
		if t_host == None:
			raise Exception("can't found a server")
		elif t_host == "NONE" or t_host == "UNALLOCATED":
			return (self.branchServer, True)
		elif t_host == "DEFAULT":
			return (self.branchServer, True)
		elif t_host.find("WEB ") != -1:
			return (self.branchServer, True)
		elif t_host.find(".") != -1:
			return (t_host, False)
		else:
			return ("whois." + t_host + ".net", False)

	def query(self, query_str):
		import re

		if self.pIpv4Part.match(query_str):
			return self.process(query_str, 4)
		elif query_str.find(":") != -1:
			return self.process(query_str, 6)
		elif query_str.find(".") != -1 or query_str.find("-") != -1:
			return self.process(query_str, 0)
		else:
			return "Sorry, query for IP or DOMAIN only"

	def process(self, query_str, ipver):
		retry = 10
		(host, branch) = self.decideServer(query_str, ipver)
		if not host:
			return "failed to choose server"
		port = 43
		while retry:
			retry = retry - 1
			try:
				response = self.whois(host, port, query_str)
			except:
				return "failed"

			if not response:
				if branch: # if branch is tried
					return "failed or reserved"
				else:
					host = self.branchServer
					branch = True
			m = self.preferral.search(response)
			if m:
				self.Debug(response)
				self.Debug(m.group(0))
				host = m.group(1).strip()
				port = int(m.group(2) or 43)
				continue

			result = []
			dones = {}

			matches = self.pdata.findall(response)
			if matches:
				for m in matches:
					(line, key) = m
					if not dones.has_key(key):
						dones[key] = True
						result.append(line)
			if not result:
				self.Debug(response)
			result = "\r\n".join(result) or "no match result"
			retry = False
		try:
			old = None
			while old != result:
				old = result
				result = result.decode('hz').encode('gbk')
		except Exception:
			pass
		result = result.decode("gbk")
		return result

	def whois(self, server, port, q):
		import socket
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.Debug("connecting %s:%d" % (server, port))
		s.connect((server, port))
		s.send(q + "\r\n")

		response = ''
		while True:
			data = s.recv(1024)
			if not data: break
			response += data
		s.close()
		if response.find("No match found for") != -1:
			return False
		return response.replace("\r", "")

if __name__ == '__main__':
	w = whois()
	print w.decideServer("61.182.208.0", 4)
	print w.decideServer("61.182.208", 4)
	print w.decideServer("61.182.", 4)
	print w.decideServer("61.", 4)
	print w.decideServer("2001:470:1f00:1459:200:f8ff:fe7a:3d5", 6)
	print w.decideServer("test.com", 0)

# vim:fdm=marker:ts=4
