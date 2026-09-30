set define on
   define OFFICE_EROC=&1
declare
   type office_list_t is table of varchar2(16);

   procedure add_full_admin(p_user varchar2, p_offices office_list_t) is
   begin
      for i in 1 .. p_offices.count loop
            cwms_sec.add_cwms_user(p_user, NULL, p_offices(i));
            cwms_sec.add_user_to_group(p_user, 'All Users',        p_offices(i));
            cwms_sec.add_user_to_group(p_user, 'CWMS Users',       p_offices(i));
            cwms_sec.add_user_to_group(p_user, 'TS ID Creator',    p_offices(i));
            cwms_sec.add_user_to_group(p_user, 'CWMS User Admins', p_offices(i));
            cwms_sec.add_user_to_group(p_user, 'CWMS PD Users',    p_offices(i));
         end loop;
   end;
begin
   cwms_sec.add_user_to_group('&&OFFICE_EROC.webtest','All Users', 'HQ');
   cwms_sec.add_user_to_group('&&OFFICE_EROC.webtest','All Users', 'SPK');
   cwms_sec.add_user_to_group('&&OFFICE_EROC.webtest','All Users', 'MVP');
   cwms_sec.add_user_to_group('&&OFFICE_EROC.webtest','All Users', 'LRL');
   cwms_sec.add_user_to_group('&&OFFICE_EROC.webtest','CWMS Users', 'HQ');
   cwms_sec.add_user_to_group('&&OFFICE_EROC.webtest','CWMS User Admins', 'HQ');
   cwms_sec.add_user_to_group('&&OFFICE_EROC.webtest','CWMS PD Users', 'HQ');


   execute immediate 'grant execute on cwms_20.cwms_upass to web_user';

   add_full_admin('M5HECTEST', office_list_t('SWT'));

   add_full_admin('s0hectest', office_list_t('LRL', 'SPK', 'MVP', 'SWT'));

   commit;

   cwms_sec.add_cwms_user('Q0HECTEST', NULL, 'HQ');
   cwms_sec.add_user_to_group('Q0HECTEST', 'All Users', 'HQ');

   delete from cwms_20.at_api_keys where key_name IN ('testkey', 'testkey2', 'non_admin_test_key');

   insert into cwms_20.at_api_keys (userid, key_name, apikey, created, expires) values ('Q0HECTEST', 'testkey', 'ak1_CYflBX6c$argon2id$v=19$m=19456,t=2,p=1$8Wh8X9m+O81UvrbCJ/eOFQ$+E0Rp3jhjduIHxaqmzx+OLR43B3HdcMuDyn8cO5/69s', sysdate, sysdate + 365);
   -- key is  ak1_CYflBX6cQOHlJkkcsA6NPvJ7npm1kynzfUsa45ncIPcGNewkcvK2ounQN8MaDj8Wkc8o0HiZvLkETpGrGkl3OvJD9Nt0vQCIPLBeqQiLGBQHsPDZmk1gEkVCzubSyfKy31bagcf0jrajn6zCcRAv1tpMpnucFCkUwCpTYwNCfCnPkqukNVpOyTv7I2II8NIxBQmQOZPc09yOrKPkQpj1sHM4NNxIcUfTZrPpidT1QGjhfVaaWW1AiqodkxXPxlTqvuRLz9bL

   insert into cwms_20.at_api_keys (userid, key_name, apikey, created, expires) values ('M5HECTEST', 'testkey2', 'ak1_SZUNxN3n$argon2id$v=19$m=19456,t=2,p=1$KAlZGdgEboEHvEVcpNGD0g$pPCCkQfOx8v5HNpwPadJNUHGI0I40a7HgcZ7JsTE6T0', sysdate, sysdate + 365);
   -- key is  ak1_SZUNxN3nDx0NpUfOJxpOuGqbqRKdYjbx86x6YVISLb9DiBi3Io5o6T6UFvkHknjIRnRO6oQfA1q6rP4XRDYMH9Hlr4ndffL6NjxPUaBZLSnqukV0uGuZKOUWBB04L5SyloJniOHkFe6ymvB9tzeziGYwzrDv3k6lzacG9vftHkCHB1QbjwwCC0sDkFvuwCe9qnyx5us11qL0YAfKXhe0fBCA2TmNDz8WXfw1HfBnAKx6WD7KqHngplWu4miOvkNverxFmAdJ
   commit;
end;
/
quit;
